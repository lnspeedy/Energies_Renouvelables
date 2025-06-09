import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000",
});

export async function getSources() {
  const { data } = await apiClient.get("/sources");
  return data;
}

export async function getData(source, params) {
  const { data } = await apiClient.get(`/data/${source}`, { params });
  return data;
}
