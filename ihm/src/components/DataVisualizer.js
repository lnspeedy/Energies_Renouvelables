import React from "react";
import { Box } from "@chakra-ui/react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar } from "recharts";

export default function DataVisualizer({ data }) {
  if (!data || data.length === 0) return null;
  const keys = Object.keys(data[0]);

  const hasLatLon = keys.includes("latitude") && keys.includes("longitude");
  if (hasLatLon) {
    return (
      <Box h="400px" w="100%" mt={4}>
        <MapContainer center={[0, 0]} zoom={2} style={{ height: "100%" }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {data.map((d, idx) => (
            <Marker key={idx} position={[d.latitude, d.longitude]}>
              <Popup>{keys.map(k => `${k}: ${d[k]}`).join("\n")}</Popup>
            </Marker>
          ))}
        </MapContainer>
      </Box>
    );
  }

  const dateCol = keys.find(k => k.toLowerCase().includes("date"));
  const numericCol = keys.find(k => typeof data[0][k] === "number" && k !== dateCol);

  if (dateCol && numericCol) {
    return (
      <LineChart width={600} height={300} data={data} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={dateCol} />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey={numericCol} stroke="#3182CE" />
      </LineChart>
    );
  }

  const catCol = keys.find(k => typeof data[0][k] === "string");
  if (catCol && numericCol) {
    return (
      <BarChart width={600} height={300} data={data} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={catCol} />
        <YAxis />
        <Tooltip />
        <Bar dataKey={numericCol} fill="#3182CE" />
      </BarChart>
    );
  }

  return null;
}

