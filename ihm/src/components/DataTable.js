import React, { useState } from "react";
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Button,
  Flex,
} from "@chakra-ui/react";

export default function DataTable({ data }) {
  const [page, setPage] = useState(0);
  const pageSize = 20;
  if (!data || data.length === 0) return null;
  const keys = Object.keys(data[0]);
  const maxPage = Math.ceil(data.length / pageSize);
  const slice = data.slice(page * pageSize, (page + 1) * pageSize);

  return (
    <TableContainer>
      <Table size="sm">
        <Thead>
          <Tr>
            {keys.map(k => (
              <Th key={k}>{k}</Th>
            ))}
          </Tr>
        </Thead>
        <Tbody>
          {slice.map((row, idx) => (
            <Tr key={idx}>
              {keys.map(k => (
                <Td key={k}>{row[k]}</Td>
              ))}
            </Tr>
          ))}
        </Tbody>
      </Table>
      <Flex justify="center" mt={2} gap={2}>
        <Button
          size="sm"
          onClick={() => setPage(p => Math.max(p - 1, 0))}
          isDisabled={page === 0}
        >
          Précédent
        </Button>
        <Button
          size="sm"
          onClick={() => setPage(p => Math.min(p + 1, maxPage - 1))}
          isDisabled={page >= maxPage - 1}
        >
          Suivant
        </Button>
      </Flex>
    </TableContainer>
  );
}

