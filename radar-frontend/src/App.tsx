import React, { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, Circle, Marker, useMap } from "react-leaflet";
import { LatLngExpression, Map as LeafletMap, Icon } from "leaflet";
import "leaflet/dist/leaflet.css";

// Helsinki city center
const HELSINKI_CENTER: LatLngExpression = [60.1699, 24.9384];
const NFZ_RADIUS_METERS = 1000; // 1km

type Drone = {
	id: string;
	x: number;
	y: number;
	z: number;
	owner_id: number;
};

// Convert your x/y to lat/lon (example: 1 unit = 1 meter, origin at Helsinki)
function xyToLatLng(x: number, y: number): LatLngExpression {
	const lat = 60.1699 + y / 111320;
	const lng = 24.9384 + x / 55800;
	return [lat, lng];
}

// Check if drone is inside NFZ (red if inside, blue if outside)
function isInNFZ(x: number, y: number, radius = 1000) {
	return Math.sqrt(x * x + y * y) <= radius;
}

// SVG icons as data URLs (bigger: 40x40)
const redDot =
	"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40'><circle cx='20' cy='20' r='16' fill='%23ff1744' stroke='white' stroke-width='4'/></svg>";
const blueDot =
	"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40'><circle cx='20' cy='20' r='16' fill='%23007bff' stroke='white' stroke-width='4'/></svg>";

const redIcon = new Icon({
	iconUrl: redDot,
	iconSize: [40, 40],
	iconAnchor: [20, 20],
});
const blueIcon = new Icon({
	iconUrl: blueDot,
	iconSize: [40, 40],
	iconAnchor: [20, 20],
});

// RadarRay that matches the NFZ circle on the map
function RadarRay({ angle, map }: { angle: number; map: LeafletMap | null }) {
	const [centerPx, setCenterPx] = useState<{ x: number; y: number } | null>(
		null,
	);
	const [radiusPx, setRadiusPx] = useState<number>(0);

	useEffect(() => {
		if (!map) return;
		const center = map.latLngToContainerPoint(HELSINKI_CENTER);
		const edge = map.latLngToContainerPoint([
			60.1699 + NFZ_RADIUS_METERS / 111320,
			24.9384,
		]);
		const r = Math.sqrt(
			(center.x - edge.x) ** 2 + (center.y - edge.y) ** 2,
		);
		setCenterPx(center);
		setRadiusPx(r);
	}, [map, map?.getZoom(), map?.getCenter()]);

	if (!centerPx || !radiusPx) return null;

	const rad = (angle * Math.PI) / 180;
	const x2 = centerPx.x + radiusPx * Math.cos(rad);
	const y2 = centerPx.y + radiusPx * Math.sin(rad);

	return (
		<svg
			style={{
				position: "absolute",
				left: 0,
				top: 0,
				pointerEvents: "none",
				zIndex: 500,
			}}
			width={window.innerWidth}
			height={window.innerHeight}
		>
			<circle
				cx={centerPx.x}
				cy={centerPx.y}
				r={radiusPx}
				fill="none"
				stroke="#00bcd4"
				strokeWidth={2}
			/>
			<line
				x1={centerPx.x}
				y1={centerPx.y}
				x2={x2}
				y2={y2}
				stroke="#00bcd4"
				strokeWidth={4}
				opacity={0.5}
			/>
			<path
				d={`
          M ${centerPx.x} ${centerPx.y}
          L ${centerPx.x + radiusPx * Math.cos(rad - 0.1)} ${centerPx.y + radiusPx * Math.sin(rad - 0.1)}
          A ${radiusPx} ${radiusPx} 0 0 1 ${centerPx.x + radiusPx * Math.cos(rad + 0.1)} ${centerPx.y + radiusPx * Math.sin(rad + 0.1)}
          Z
        `}
				fill="#00bcd4"
				opacity={0.15}
			/>
		</svg>
	);
}

function RadarRayWrapper({ angle }: { angle: number }) {
	const map = useMap();
	return <RadarRay angle={angle} map={map} />;
}

const NFZCircle = () => (
	<Circle
		center={HELSINKI_CENTER}
		radius={NFZ_RADIUS_METERS}
		pathOptions={{ color: "#00bcd4" }}
	/>
);

function App() {
	const [drones, setDrones] = useState<Drone[]>([]);
	const [angle, setAngle] = useState(0);
	const animationRef = useRef<number | null>(null);

	// Animate radar ray
	useEffect(() => {
		function animate() {
			setAngle((a) => (a + 2) % 360);
			animationRef.current = requestAnimationFrame(animate);
		}
		animationRef.current = requestAnimationFrame(animate);
		return () => {
			if (animationRef.current)
				cancelAnimationFrame(animationRef.current);
		};
	}, []);

	// Fetch drones every second
	const fetchDrones = () => {
		fetch("http://localhost:8000/drones")
			.then((res) => res.json())
			.then((data) => setDrones(data.drones || []));
	};

	useEffect(() => {
		fetchDrones();
		const interval = setInterval(fetchDrones, 1000);
		return () => clearInterval(interval);
	}, []);

	return (
		<div style={{ height: "100vh", width: "100vw" }}>
			<button
				style={{
					position: "absolute",
					zIndex: 1000,
					top: 10,
					left: 10,
				}}
				onClick={fetchDrones}
			>
				Update
			</button>
			<MapContainer
				center={HELSINKI_CENTER}
				zoom={13}
				style={{ height: "100vh", width: "100vw" }}
				dragging={false}
				zoomControl={false}
				scrollWheelZoom={false}
				doubleClickZoom={false}
				boxZoom={false}
				keyboard={false}
			>
				<TileLayer
					url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
					attribution="&copy; OpenStreetMap contributors"
				/>
				<NFZCircle />
				{drones.map((d) => (
					<Marker
						key={d.id}
						position={xyToLatLng(d.x, d.y)}
						icon={isInNFZ(d.x, d.y) ? redIcon : blueIcon}
					/>
				))}
				<RadarRayWrapper angle={angle} />
			</MapContainer>
		</div>
	);
}

export default App;
