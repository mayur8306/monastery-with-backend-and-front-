import { useEffect, useRef } from "react";
import Marzipano from "marzipano";

export default function PanoramaViewer({ imageUrl }) {
  const panoRef = useRef();

  useEffect(() => {
    if (!imageUrl) return;
    const viewer = new Marzipano.Viewer(panoRef.current);
    const source = Marzipano.ImageUrlSource.fromString(imageUrl);
    const geometry = new Marzipano.EquirectGeometry([{ width: 4000 }]);
    const limiter = Marzipano.RectilinearView.limit.traditional(1024, 100 * Math.PI / 180);
    const view = new Marzipano.RectilinearView(null, limiter);
    const scene = viewer.createScene({ source, geometry, view });
    scene.switchTo();
  }, [imageUrl]);

  return <div ref={panoRef} style={{ width: "100%", height: "400px" }} />;
}

