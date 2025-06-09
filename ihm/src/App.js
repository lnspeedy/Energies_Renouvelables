import React, { useEffect, useState } from "react";
import {
  ChakraProvider,
  Box,
  Heading,
  Select,
  Card,
  CardHeader,
  CardBody,
  extendTheme,
  IconButton,
  useColorMode,
} from "@chakra-ui/react";
import { SunIcon, MoonIcon } from "@chakra-ui/icons";
import { getSources, getData } from "./api";
import DataTable from "./components/DataTable";
import FilterPanel from "./components/FilterPanel";
import DataVisualizer from "./components/DataVisualizer";

function ColorModeSwitcher() {
  const { colorMode, toggleColorMode } = useColorMode();
  return (
    <IconButton
      onClick={toggleColorMode}
      icon={colorMode === "light" ? <MoonIcon /> : <SunIcon />}
      aria-label="Toggle color mode"
      position="absolute"
      top={2}
      right={2}
    />
  );
}

const theme = extendTheme({
  config: { initialColorMode: "light", useSystemColorMode: false },
  colors: { brand: { 500: "#2B6CB0" } },
});

export default function App() {
  const [sources, setSources] = useState([]);
  const [selected, setSelected] = useState("");
  const [filters, setFilters] = useState({});
  const [records, setRecords] = useState([]);

  useEffect(() => {
    getSources().then(setSources).catch(console.error);
  }, []);

  const fetchData = () => {
    if (!selected) return;
    getData(selected, filters)
      .then(res => setRecords(res.data))
      .catch(console.error);
  };

  return (
    <ChakraProvider theme={theme}>
      <Box maxW="7xl" mx="auto" p={4} position="relative">
        <ColorModeSwitcher />
        <Heading mb={4}>Explorateur d\u00e9nergies renouvelables</Heading>
        <Card mb={4}>
          <CardHeader>
            <Select
              placeholder="Choisir une source"
              value={selected}
              onChange={e => setSelected(e.target.value)}
            >
              {sources.map(s => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </Select>
          </CardHeader>
          <CardBody>
            <FilterPanel filters={filters} onChange={setFilters} onApply={fetchData} />
          </CardBody>
        </Card>
        <DataVisualizer data={records} />
        <DataTable data={records} />
      </Box>
    </ChakraProvider>
  );
}

