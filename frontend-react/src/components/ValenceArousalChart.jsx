import React, { useEffect, useRef } from "react";
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Title,
} from "chart.js";
import { Scatter } from "react-chartjs-2";

ChartJS.register(
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Title
);

export default function ValenceArousalChart({ data }) {
  const chartRef = useRef(null);

  const prepareChartData = () => {
    const songs = data.valence_arousal_analysis.songs;

    // Separamos las canciones por fuente
    const bothData = [];
    const audioOnlyData = [];
    const lyricsOnlyData = [];

    songs.forEach((song) => {
      const ponit = {
        x: song.valence,
        y: song.arousal,
        title: song.title,
        artist: song.artist,
        dataSource: song.data_source,
      };

      if (song.data_source === "both") {
        bothData.push(ponit);
      } else if (song.data_source === "audio_only") {
        audioOnlyData.push(ponit);
      } else {
        lyricsOnlyData.push(ponit);
      }
    });
    
  };

  return <div></div>;
}
