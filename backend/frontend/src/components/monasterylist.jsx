import { useEffect, useState } from "react";
import { fetchMonasteries } from "../api";

export default function MonasteryList() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchMonasteries().then(res => setData(res.data));
  }, []);

  return (
    <div>
      <h2>Monasteries</h2>
      <ul>
        {data.map(m => (
          <li key={m.id}>
            {m.name} ({m.gps_lat}, {m.gps_lon}) - Elevation: {m.elevation || 'N/A'}
          </li>
        ))}
      </ul>
    </div>
  );
}
