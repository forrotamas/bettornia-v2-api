from app.adapters.registry import register
from app.adapters.echo_adapter import EchoAdapter
from app.adapters.pinnacle_like_adapter import PinnacleLikeAdapter

def init_adapters() -> None:
    register(EchoAdapter())
    register(PinnacleLikeAdapter())
