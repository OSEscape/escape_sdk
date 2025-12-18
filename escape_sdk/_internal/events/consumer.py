"""
Inotify-based event consumer for RuneLite events.

Watches /dev/shm/runelite_doorbell using inotify for instant event notifications.
Processes ring buffer and latest-state channels, updates cache.
Runs in background thread.

Requirements:
- Linux with inotify support (required, no fallback)
- RuneLite with Escape plugin running (creates doorbell)
"""

import glob
import logging
import os
import threading
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

import msgpack
from inotify_simple import INotify
from inotify_simple import flags as inotify_flags

from .channels import (
    DOORBELL_PATH,
    LATEST_STATE_CHANNELS,
    RING_BUFFER_CHANNELS,
    SHM_DIR,
)


class EventConsumer:
    """
    Consumes events from /dev/shm using inotify doorbell pattern.

    Architecture:
    - Watches doorbell file with inotify (zero CPU when idle)
    - Wakes instantly when doorbell is rung
    - Processes all pending ring buffer and latest-state events
    - Updates cache with event data
    - Runs in background daemon thread
    """

    def __init__(self, cache, warn_on_gaps: bool = True):
        """
        Initialize event consumer.

        Args:
            cache: EventCache instance to update
            warn_on_gaps: Warn when ring buffer sequence gaps detected
        """
        self.cache = cache
        self.warn_on_gaps = warn_on_gaps

        # Tracking state
        self.last_seq = defaultdict(int)  # Last processed sequence per channel
        self.last_state_mtime = defaultdict(float)  # Last mtime per state channel

        # Thread control
        self.running = False
        self.thread: threading.Thread | None = None

        # Warmup tracking
        self._warmup_complete = threading.Event()
        self._warmup_event_count = 0

        # Inotify setup
        self.inotify: INotify | None = None
        self._setupInotify()

    def _setupInotify(self) -> None:
        """Setup inotify watch on doorbell file."""
        self.inotify = INotify()

        # Check if doorbell exists
        if not os.path.exists(DOORBELL_PATH):
            logger.warning("Doorbell not found at %s", DOORBELL_PATH)
            logger.info("Waiting for Java plugin to create it...")
            # Wait up to 5 seconds for doorbell to appear
            for _ in range(50):
                if os.path.exists(DOORBELL_PATH):
                    break
                time.sleep(0.1)

        if not os.path.exists(DOORBELL_PATH):
            raise FileNotFoundError(
                f"Doorbell not found at {DOORBELL_PATH}. "
                f"Make sure RuneLite is running with Escape plugin."
            )

        # Watch for modifications and close-write events
        self.inotify.add_watch(DOORBELL_PATH, inotify_flags.MODIFY | inotify_flags.CLOSE_WRITE)
        logger.info("Watching doorbell: %s", DOORBELL_PATH)

    def start(self, wait_for_warmup: bool = True, warmup_timeout: float = 5.0) -> bool:
        """
        Start background event consumer thread.

        Args:
            wait_for_warmup: If True, block until initial event processing completes
            warmup_timeout: Maximum seconds to wait for warmup (default 5.0)

        Returns:
            True if started successfully
        """
        if self.running:
            logger.info("Event consumer already running")
            return False

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True, name="EventConsumer")
        self.thread.start()

        logger.info("Event consumer started (inotify mode)")

        # Process initial backlog of events before continuing
        if wait_for_warmup:
            return self.waitForWarmup(timeout=warmup_timeout)

        return True

    def waitForWarmup(self, timeout: float = 5.0) -> bool:
        """
        Wait for initial warmup phase to complete.

        Blocks until all existing events are processed or timeout occurs.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if warmup completed, False if timeout
        """
        if self._warmup_complete.wait(timeout=timeout):
            return True
        else:
            logger.warning(
                "Warmup timeout after %ss (processed %d events)",
                timeout,
                self._warmup_event_count,
            )
            return False

    def stop(self) -> None:
        """Stop event consumer thread."""
        if not self.running:
            return

        logger.info("Stopping event consumer...")
        self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)

        if self.inotify:
            self.inotify.close()

        logger.info("Event consumer stopped")

    def _run(self) -> None:
        """Main event loop - runs in background thread."""
        logger.debug("Event consumer loop started")
        logger.debug("Ring buffer channels: %s", ", ".join(RING_BUFFER_CHANNELS))
        logger.debug("Latest-state channels: %s", ", ".join(LATEST_STATE_CHANNELS))

        # Perform initial warmup - process all existing events before entering main loop
        self._performWarmup()

        while self.running:
            try:
                # Block here until doorbell rings (zero CPU usage!)
                events = self.inotify.read(timeout=1000)  # 1s timeout for clean shutdown

                if events:
                    # Doorbell was rung! Process all channels
                    self._processAllChannels()

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.exception("Error in event loop: %s", e)
                time.sleep(1)

    def _performWarmup(self) -> None:
        """
        Process all existing events during startup (warmup phase).

        This ensures the cache is populated before the main script continues.
        """
        logger.debug("Warming up event cache...")
        start_time = time.time()
        total_events = 0

        # Process all ring buffer channels
        for channel in RING_BUFFER_CHANNELS:
            count = self._processRingBuffer(channel)
            total_events += count

        # Process all latest-state channels
        for channel in LATEST_STATE_CHANNELS:
            self._processLatestState(channel)

        # Calculate stats
        elapsed_ms = (time.time() - start_time) * 1000
        per_event_us = (elapsed_ms * 1000) / total_events if total_events > 0 else 0

        # Store count for timeout reporting
        self._warmup_event_count = total_events

        if total_events > 0:
            logger.info(
                "Warmup complete: processed %d events in %.1f ms (%.0fus/event)",
                total_events,
                elapsed_ms,
                per_event_us,
            )
        else:
            logger.debug("Warmup complete: no backlog events found")

        # Signal that warmup is complete
        self._warmup_complete.set()

    def _processAllChannels(self) -> None:
        """Process all ring buffer and latest-state channels."""
        start_time = time.time()
        total_events = 0

        # Process ring buffer channels (guaranteed delivery)
        for channel in RING_BUFFER_CHANNELS:
            count = self._processRingBuffer(channel)
            total_events += count

        # Process latest-state channels (current state only)
        for channel in LATEST_STATE_CHANNELS:
            self._processLatestState(channel)

        # Log if we processed more than 10 events
        if total_events > 10:
            elapsed_ms = (time.time() - start_time) * 1000
            per_event_us = (elapsed_ms * 1000) / total_events if total_events > 0 else 0
            logger.debug(
                "Cleared %d events in %.1f ms (%.0fus/event)",
                total_events,
                elapsed_ms,
                per_event_us,
            )

    def _processRingBuffer(self, channel: str) -> int:
        """
        Process ring buffer events for a channel.

        Files: /dev/shm/{channel}.{seq}

        Args:
            channel: Channel name

        Returns:
            Number of events processed
        """
        pattern = f"{SHM_DIR}/{channel}.*"
        files = sorted(
            glob.glob(pattern),
            key=lambda x: int(x.split(".")[-1]) if x.split(".")[-1].isdigit() else 0,
        )

        events_processed = 0

        for filepath in files:
            try:
                # Extract sequence number
                filename = os.path.basename(filepath)
                parts = filename.split(".")
                if len(parts) < 2 or not parts[-1].isdigit():
                    continue

                seq = int(parts[-1])

                # Skip if already processed
                if seq <= self.last_seq[channel]:
                    os.remove(filepath)
                    continue

                # Read and deserialize event
                with open(filepath, "rb") as f:
                    event = msgpack.unpackb(f.read(), raw=False, strict_map_key=False)

                # Verify sequence continuity
                expected_seq = self.last_seq[channel] + 1
                if seq != expected_seq and self.last_seq[channel] > 0:
                    if self.warn_on_gaps:
                        gap_size = seq - expected_seq
                        logger.warning(
                            "[%s] Gap detected! Expected %d, got %d (missed %d)",
                            channel,
                            expected_seq,
                            seq,
                            gap_size,
                        )

                self.cache.addEvent(channel, event)

                # Update sequence tracker
                self.last_seq[channel] = seq
                events_processed += 1

                # Delete processed event
                os.remove(filepath)

            except Exception as e:
                logger.error("Error processing %s: %s", filepath, e)

        return events_processed

    def _processLatestState(self, channel: str) -> bool:
        """
        Process latest-state event for a channel.

        Files: /dev/shm/{channel}

        Args:
            channel: Channel name

        Returns:
            True if state was updated
        """
        filepath = f"{SHM_DIR}/{channel}"

        try:
            if not os.path.exists(filepath):
                return False

            # Check if file was modified since last read
            stat = os.stat(filepath)
            current_mtime = stat.st_mtime

            # Skip if file hasn't changed
            if current_mtime <= self.last_state_mtime[channel]:
                return False

            # Update modification time tracker
            self.last_state_mtime[channel] = current_mtime

            # Read and deserialize state
            with open(filepath, "rb") as f:
                state = msgpack.unpackb(f.read(), raw=False, strict_map_key=False)

            # Update cache - all latest-state events use same method now
            self.cache.addEvent(channel, state)

            return True

        except Exception as e:
            logger.error("Error reading %s: %s", filepath, e)
            return False
