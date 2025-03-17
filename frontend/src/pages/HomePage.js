import React, { useState, useEffect } from 'react';
import HeroSection from '../components/HeroSection';
import './HomePage.css';

import axios from 'axios';
import Marquee from "react-fast-marquee";


const HomePage = () => {

  const [trendingTopics, setTrendingTopics] = useState([]);
  const [trendingLoading, setTrendingLoading] = useState(true);

  // Fetch trendline data from the backend API once on mount, then update every 60 seconds.


  useEffect(() => {
    const fetchTrendingTopics = async () => {
      try {
        const res = await axios.get('http://localhost:5000/api/trending');
        // Expected response: { timestamp: string, trending_topics: [ 'topic1', 'topic2', ... ] }
        setTrendingTopics(res.data.trending_topics);
        setTrendingLoading(false);
      } catch (error) {
        console.error("Error fetching trending topics:", error);
        setTrendingLoading(false);
      }
    };

    fetchTrendingTopics();
    const trendingIntervalId = setInterval(fetchTrendingTopics, 600000); // update every 10 minutes
    return () => clearInterval(trendingIntervalId);
  }, []);



  return (
    <div className="container">
      <HeroSection />
      <div className="marquee-container">
        <div className="marquee-box">
          <Marquee className="marquee" pauseOnHover={true} >
              <h5>{trendingLoading
              ? "Loading trending topics..."
              : trendingTopics.map((topic, index) => (
            <span key={index} style={{ marginRight: '40px', fontFamily: 'sans-serif' }}>
              {topic}
            </span>
                ))
              }</h5>
          </Marquee>
        </div>
      </div>



    </div>
  );
};

export default HomePage;
