"""Anomaly detector: matches logs against known issues or flags true anomalies."""

from typing import Dict, Optional, Union

from app.state import GraphState

KNOWN_ISSUES: Dict[str, str] = {
    "interface timeout": (
        "Check physical cabling and SFP modules on the affected interface. "
        "Verify duplex/speed settings match the peer. If flapping persists, "
        "replace the transceiver or move the link to a spare port."
    ),
    "interface timed out": (
        "Check physical cabling and SFP modules on the affected interface. "
        "Verify duplex/speed settings match the peer. If flapping persists, "
        "replace the transceiver or move the link to a spare port."
    ),
    "bgp neighbor down": (
        "Verify BGP peer IP reachability and that the hold timer has not expired. "
        "Check AS number, authentication keys, and inbound/outbound route policies. "
        "Reset the BGP session after confirming the peer device is healthy."
    ),
    "hold timer expired": (
        "Verify BGP peer IP reachability and that the hold timer has not expired. "
        "Check AS number, authentication keys, and inbound/outbound route policies. "
        "Reset the BGP session after confirming the peer device is healthy."
    ),
    "ospf adjacency failure": (
        "Confirm OSPF area IDs, network types, and hello/dead timers match on both sides. "
        "Check for MTU mismatches and ACLs blocking protocol traffic. "
        "Clear the OSPF process on the affected interface if config is correct."
    ),
    "memory threshold exceeded": (
        "Identify memory-heavy processes with 'show processes memory'. "
        "Clear unused BGP routes or reduce logging verbosity. "
        "Schedule a maintenance window to reload if memory does not recover."
    ),
    "ntp sync failure": (
        "Verify NTP server reachability and that UDP port 123 is permitted. "
        "Check stratum configuration and authentication keys. "
        "Point to a reachable stratum-1/2 server or enable the hardware clock as fallback."
    ),
    "cpu spike": (
        "Inspect 'show processes cpu sorted' for the top consumer. "
        "Disable unnecessary debug logging and limit SNMP polling frequency. "
        "If caused by routing churn, stabilize BGP/OSPF peers before further investigation."
    ),
    "power supply alert": (
        "Confirm redundant power supplies are seated and receiving AC/DC input. "
        "Replace the failed PSU module immediately to restore redundancy. "
        "Check environmental sensors for overheating or airflow blockage."
    ),
    "stp topology change": (
        "Identify the port triggering the TCN with 'show spanning-tree detail'. "
        "Verify edge/portfast settings on access ports and remove rogue switches. "
        "Stabilize the link or disable the flapping port to prevent broadcast storms."
    ),
}


def detect_anomaly(state: GraphState) -> Dict[str, Union[str, bool, None]]:
    """Match log text against known issues or mark as a true anomaly."""
    log_lower = state["raw_log"].lower()

    for keyword, fix in KNOWN_ISSUES.items():
        if keyword in log_lower:
            return {
                "anomaly_status": "KNOWN_ISSUE",
                "known_fix": fix,
                "should_continue": False,
            }

    return {
        "anomaly_status": "TRUE_ANOMALY",
        "known_fix": None,
        "should_continue": True,
    }
