import axios from "axios";

const api = axios.create({
  baseURL: "/api/",  // relative URL, works with Django serving React
});

export const fetchMonasteries = () => api.get("monasteries/");
export const uploadPanorama = (data) => api.post("upload-panorama/", data);
export const matchImage = (data) => api.post("match-image/", data);

export default api;
