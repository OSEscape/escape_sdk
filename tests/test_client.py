"""Tests for the main Client class."""

from escape.client import Client


class TestClient:
    """Test suite for Client class."""

    def test_client_initialization(self):
        """Test that client initializes properly."""
        client = Client()
        assert client is not None
        assert not client.isConnected()

    def test_client_connection(self, client):
        """Test client connection."""
        assert not client.isConnected()
        result = client.connect()
        assert result is True
        assert client.isConnected()

    def test_client_disconnection(self, connected_client):
        """Test client disconnection."""
        assert connected_client.isConnected()
        connected_client.disconnect()
        assert not connected_client.isConnected()
