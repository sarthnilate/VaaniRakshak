"""
============================================================
VAANIRAKSHAK — Carrier SIP Trunk & CDR Telephony Adapter
============================================================
Provides integration interfaces for Telecom Carriers (Tier 3 Operator Mode):
  - Ingests SIP trunk signaling events (INVITE, RTP stream initialization).
  - Enriches call sessions with Carrier-grade Call Detail Record (CDR) network telemetry.
  - Dispatches automated SIP BYE / Call Teardown commands on high-confidence fraud.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid


INDIAN_FRAUD_HOTSPOTS = [
    {
        "hotspot_id": "HOTSPOT-JAMTARA-01",
        "region_name": "Jamtara Cyber Belt (Jharkhand)",
        "latitude": 23.9629,
        "longitude": 86.8016,
        "risk_index": 96,
        "primary_modus_operandi": "OTP Harvesting, SIM Swap, Emergency Cloned Extortion",
        "active_sim_farms": 142,
        "status": "CRITICAL_MONITORING",
    },
    {
        "hotspot_id": "HOTSPOT-MEWAT-02",
        "region_name": "Nuh / Mewat Tri-State Grid (Haryana)",
        "latitude": 28.1091,
        "longitude": 77.0094,
        "risk_index": 92,
        "primary_modus_operandi": "CBI / Police Digital Arrest Impersonation",
        "active_sim_farms": 118,
        "status": "HIGH_ALERT",
    },
    {
        "hotspot_id": "HOTSPOT-ALWAR-03",
        "region_name": "Alwar Regional Cluster (Rajasthan)",
        "latitude": 27.5645,
        "longitude": 76.6111,
        "risk_index": 88,
        "primary_modus_operandi": "Fake Vehicle Sale & Military Impersonation",
        "active_sim_farms": 76,
        "status": "ELEVATED_WATCH",
    },
    {
        "hotspot_id": "HOTSPOT-NCR-04",
        "region_name": "Delhi NCR Northern Hub (Noida/Rohini)",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "risk_index": 84,
        "primary_modus_operandi": "Bogus Telecom Tech Support & Credit Card KYC",
        "active_sim_farms": 94,
        "status": "ACTIVE_INVESTIGATION",
    },
]


@dataclass
class CellTowerLocation:
    cgi: str
    region_name: str
    latitude: float
    longitude: float
    tower_vendor: str
    signal_strength_dbm: int
    is_known_fraud_corridor: bool
    hotspot_ref: Optional[str] = None


@dataclass
class CarrierCallEvent:
    call_id: str
    calling_party: str
    called_party: str
    sip_method: str = "INVITE"
    codec: str = "AMR-WB/16000"
    cell_tower_cgi: str = "404-45-8192-3021"  # MCC-MNC-LAC-CID
    carrier_name: str = "National Telecom Grid (Tier-1)"
    packet_loss_pct: float = 0.8
    jitter_ms: float = 4.2
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tower_location: Optional[CellTowerLocation] = None


@dataclass
class CarrierTeardownResult:
    call_id: str
    status: str
    sip_response_code: int
    teardown_timestamp: str
    reason: str


class CarrierSipTrunkAdapter:
    """
    Adapter simulating Tier-3 Carrier gRPC/SIP Trunk webhook integration
    with real-time Cell Tower CGI triangulation and telecom fraud hotspot analytics.
    """

    def __init__(self, carrier_name: str = "Bharat Telecom Carrier Gateway"):
        self.carrier_name = carrier_name
        self._active_circuits: Dict[str, CarrierCallEvent] = {}
        self._seed_default_circuits()

    def _resolve_tower_location(self, cgi: str) -> CellTowerLocation:
        """Resolves Cell Global Identity (CGI) to physical coordinates and hotspot risk."""
        if "8192" in cgi:
            # Jamtara Cluster Tower
            return CellTowerLocation(
                cgi=cgi,
                region_name="Jamtara Cyber Belt, Jharkhand",
                latitude=23.9629,
                longitude=86.8016,
                tower_vendor="Ericsson RBS 6000",
                signal_strength_dbm=-78,
                is_known_fraud_corridor=True,
                hotspot_ref="HOTSPOT-JAMTARA-01",
            )
        elif "7701" in cgi:
            # Mewat/Nuh Cluster Tower
            return CellTowerLocation(
                cgi=cgi,
                region_name="Nuh / Mewat Sector 4, Haryana",
                latitude=28.1091,
                longitude=77.0094,
                tower_vendor="Nokia AirScale",
                signal_strength_dbm=-82,
                is_known_fraud_corridor=True,
                hotspot_ref="HOTSPOT-MEWAT-02",
            )
        else:
            # Default NCR / Regional Tower
            return CellTowerLocation(
                cgi=cgi,
                region_name="Delhi NCR Central Node, New Delhi",
                latitude=28.6139,
                longitude=77.2090,
                tower_vendor="Huawei BTS3900",
                signal_strength_dbm=-72,
                is_known_fraud_corridor=False,
                hotspot_ref=None,
            )

    def _seed_default_circuits(self):
        """Pre-seeds demo circuits for live SIH scenario evaluation."""
        self.register_call({
            "call_id": "sess_sih_showcase_01",
            "calling_party": "+91-9876543210",
            "called_party": "+91-9811122334",
            "cell_tower_cgi": "404-45-8192-3021",
            "codec": "AMR-WB/23850",
            "packet_loss_pct": 2.1,
            "jitter_ms": 6.4,
        })

    def register_call(self, event_data: Dict[str, Any]) -> CarrierCallEvent:
        """Registers an incoming SIP trunk call event into the carrier telemetry circuit."""
        call_id = event_data.get("call_id") or str(uuid.uuid4())
        cgi = event_data.get("cell_tower_cgi", "404-45-8192-3021")
        tower_loc = self._resolve_tower_location(cgi)

        call_event = CarrierCallEvent(
            call_id=call_id,
            calling_party=event_data.get("calling_party", "+91-UNKNOWN"),
            called_party=event_data.get("called_party", "+91-USER"),
            sip_method=event_data.get("sip_method", "INVITE"),
            codec=event_data.get("codec", "AMR-WB/16000"),
            cell_tower_cgi=cgi,
            carrier_name=self.carrier_name,
            packet_loss_pct=float(event_data.get("packet_loss_pct", 0.5)),
            jitter_ms=float(event_data.get("jitter_ms", 3.8)),
            tower_location=tower_loc,
        )
        self._active_circuits[call_id] = call_event
        return call_event

    def trigger_carrier_teardown(self, call_id: str, reason: str = "AI_VOICE_FRAUD_INTERVENTION") -> CarrierTeardownResult:
        """
        Sends an automated SIP BYE (Code 603 Decline / Emergency Release) command
        to immediately terminate the carrier telecom circuit.
        """
        circuit = self._active_circuits.pop(call_id, None)
        timestamp = datetime.now(timezone.utc).isoformat()

        if circuit:
            return CarrierTeardownResult(
                call_id=call_id,
                status="CIRCUIT_TERMINATED",
                sip_response_code=603,
                teardown_timestamp=timestamp,
                reason=reason,
            )
        else:
            return CarrierTeardownResult(
                call_id=call_id,
                status="CIRCUIT_NOT_FOUND_OR_ALREADY_CLOSED",
                sip_response_code=481,
                teardown_timestamp=timestamp,
                reason=reason,
            )

    def get_circuit_telemetry(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Returns network-level telemetry for an ACTIVE carrier circuit. Returns None if not found."""
        circuit = self._active_circuits.get(call_id)
        if not circuit:
            return None

        t_loc = circuit.tower_location or self._resolve_tower_location(circuit.cell_tower_cgi)
        return {
            "call_id": circuit.call_id,
            "carrier_name": circuit.carrier_name,
            "calling_party": circuit.calling_party,
            "called_party": circuit.called_party,
            "codec": circuit.codec,
            "cell_tower_cgi": circuit.cell_tower_cgi,
            "tower_location": {
                "region_name": t_loc.region_name,
                "latitude": t_loc.latitude,
                "longitude": t_loc.longitude,
                "tower_vendor": t_loc.tower_vendor,
                "signal_strength_dbm": t_loc.signal_strength_dbm,
                "is_known_fraud_corridor": t_loc.is_known_fraud_corridor,
                "hotspot_ref": t_loc.hotspot_ref,
            },
            "network_telemetry": {
                "packet_loss_pct": circuit.packet_loss_pct,
                "jitter_ms": circuit.jitter_ms,
                "round_trip_time_ms": 42,
                "sip_session_alive": True,
            },
        }

    def get_or_mock_circuit_telemetry(self, call_id: str) -> Dict[str, Any]:
        """Returns telemetry for an active circuit or a Jamtara demo mock for unknown/terminated sessions."""
        active = self.get_circuit_telemetry(call_id)
        if active:
            return active
        # Fallback: Jamtara demo mock for SIH demonstration purposes
        tower = self._resolve_tower_location("404-45-8192-3021")
        return {
            "call_id": call_id,
            "carrier_name": self.carrier_name,
            "calling_party": "+91-9876543210",
            "called_party": "+91-USER",
            "codec": "AMR-WB/23850",
            "cell_tower_cgi": tower.cgi,
            "tower_location": {
                "region_name": tower.region_name,
                "latitude": tower.latitude,
                "longitude": tower.longitude,
                "tower_vendor": tower.tower_vendor,
                "signal_strength_dbm": tower.signal_strength_dbm,
                "is_known_fraud_corridor": tower.is_known_fraud_corridor,
                "hotspot_ref": tower.hotspot_ref,
            },
            "network_telemetry": {
                "packet_loss_pct": 1.8,
                "jitter_ms": 5.2,
                "round_trip_time_ms": 38,
                "sip_session_alive": True,
            },
        }


    def get_fraud_hotspots(self) -> list:
        """Returns catalogue of major Indian telecom fraud clusters."""
        return INDIAN_FRAUD_HOTSPOTS


carrier_adapter = CarrierSipTrunkAdapter()

