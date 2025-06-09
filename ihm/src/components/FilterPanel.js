import React from "react";
import {
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Input,
  NumberInput,
  NumberInputField,
  Stack,
} from "@chakra-ui/react";

export default function FilterPanel({ filters, onChange, onApply }) {
  return (
    <Box as="form" onSubmit={e => e.preventDefault()} mb={4}>
      <Stack spacing={3} direction={{ base: "column", md: "row" }}>
        <FormControl>
          <FormLabel>Année début</FormLabel>
          <NumberInput
            value={filters.annee_debut || ""}
            onChange={(_, v) => onChange({ ...filters, annee_debut: v })}
          >
            <NumberInputField placeholder="ex: 2015" />
          </NumberInput>
        </FormControl>
        <FormControl>
          <FormLabel>Année fin</FormLabel>
          <NumberInput
            value={filters.annee_fin || ""}
            onChange={(_, v) => onChange({ ...filters, annee_fin: v })}
          >
            <NumberInputField placeholder="ex: 2020" />
          </NumberInput>
        </FormControl>
        <FormControl>
          <FormLabel>Pays</FormLabel>
          <Input
            value={filters.pays || ""}
            onChange={e => onChange({ ...filters, pays: e.target.value })}
            placeholder="France"
          />
        </FormControl>
        <FormControl>
          <FormLabel>Recherche</FormLabel>
          <Input
            value={filters.q || ""}
            onChange={e => onChange({ ...filters, q: e.target.value })}
            placeholder="Texte libre"
          />
        </FormControl>
        <Flex align="flex-end">
          <Button colorScheme="teal" onClick={onApply}>
            Appliquer
          </Button>
        </Flex>
      </Stack>
    </Box>
  );
}
