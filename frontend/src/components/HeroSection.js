import React, {useEffect, useState} from 'react';
import './HeroSection.css';
import sol_logo from "../assets/Sol.png";
import {TiArrowSortedDown, TiArrowSortedUp} from "react-icons/ti";
import axios from "axios";
import {Sparklines, SparklinesLine} from "react-sparklines";
import { Tooltip } from 'react-tooltip'
import { CiCircleInfo } from "react-icons/ci";
import { IconContext } from "react-icons";


const HeroSection = () => {
      const [loading, setLoading] = useState(true);
      const [trendline, setTrendline] = useState([]);


      let currentPrice = 0;
      let dayChange = 0;
      const isUp = dayChange >= 0;

      useEffect(() => {
        const fetchTrendline = async () => {
         try {
          const res = await axios.get('http://localhost:5000/api/sol_trendline');
          // Expected response: an array of objects with keys: { timestamp, price, dayChange }
          setTrendline(res.data);
           setLoading(false);
        } catch (error) {
          console.error("Error fetching trendline data:", error);
          setLoading(false);
        }
        };

        fetchTrendline();
            const intervalId = setInterval(fetchTrendline, 600000); // update every 60 seconds
            return () => clearInterval(intervalId);
        }, []);

        if (trendline.length > 0) {
        const latestRecord = trendline[trendline.length - 1];
        currentPrice = parseFloat(latestRecord.price);
        dayChange = parseFloat(latestRecord.dayChange);
    }

        const sparklineData = trendline.map(item => parseFloat(item.price));
        const [fearGreedData, setFearGreedData] = useState(null);
        const [fgLoading, setFgLoading] = useState(true);


        useEffect(() => {
    const fetchFearGreed = async () => {
      try {
        const res = await axios.get("http://localhost:5000/api/fear_vs_greed");
        // Expected response: { value: "numberString", name: "classificationString" }
        setFearGreedData(res.data);
        setFgLoading(false);
      } catch (error) {
        console.error("Error fetching fear vs greed data:", error);
        setFgLoading(false);
      }
    };

    fetchFearGreed();
  }, []);

  const fearGreedValue = fearGreedData ? parseInt(fearGreedData.value, 10) : 0;

  const [fgTrendline, setFgTrendline] = useState([]);
  useEffect(() => {
    const fetchFGTrendline = async () => {
      try {
        const res = await axios.get("http://localhost:5000/api/fear_vs_greed_trendline");
        // The API returns an object with timestamp keys and corresponding value.
        // We'll sort the timestamps and map them to an array of numbers.
        const dataObj = res.data;
        const sortedTimestamps = Object.keys(dataObj).sort();
        const trendlineArray = sortedTimestamps.map(ts => parseFloat(dataObj[ts]));
        setFgTrendline(trendlineArray);
      } catch (error) {
        console.error("Error fetching fear vs greed trendline:", error);
      }
    };

    fetchFGTrendline();
  }, []);

  return (
    <section className="hero">
      <h1>A Comprehensive Solana Intelligence Platform</h1>
      <p>Your real-time view into the latest coin metrics, social signals, and blockchain events.</p>

            <Tooltip id="my-tooltip" clickable event="click" />

        <div className="metrics">
            <div className="card">
                <div className="header-info">
                    <img src={sol_logo} className="sol_image" alt="Sol"/>
                    <h2>Solana</h2>
                    <h3>SOL</h3>
                </div>
                <div className="price-info">
                    {loading ? (
                        <p>Loading...</p>
                    ) : (
                        <>
                            <h2>${currentPrice.toFixed(2)}</h2>
                            <div className="price-change">
                                {isUp ? (
                                    <TiArrowSortedUp style={{color: "green"}}/>
                                ) : (
                                    <TiArrowSortedDown style={{color: "red"}}/>
                                )}
                                <span style={{color: isUp ? "green" : "red"}}>
                  {isUp ? "+" : "-"}{Math.abs(dayChange).toFixed(2)}%
                </span>
                            </div>
                        </>
                    )}
                </div>
                <div className="sparkLine">
                    {sparklineData.length > 0 ? (
                        <Sparklines data={sparklineData} margin={6}>
                            <SparklinesLine style={{fill: "none"}} color="lightblue"/>
                        </Sparklines>
                    ) : (
                        <p><Sparklines data={[10, 5, 15, 20]} margin={6}>
                            <SparklinesLine style={{fill: "none"}} color="lightblue"/>
                        </Sparklines>
                        </p>
                    )}
                </div>
            </div>
            <div className="card">
                <div className="heading">
                <h2>Fear vs Greed Index</h2>
                <button
                    type="button"
                    data-tooltip-id="my-tooltip"
                    data-tooltip-html="<div>When the value is closer to 0</div> <div> the market is in Extreme Fear </div> <div> and investors have over-sold</div> <div>  irrationally. </div>"
                    data-tooltip-place="bottom"
                    style={{background: 'none', border: 'none', marginLeft: '0.5rem', cursor: 'pointer'}}
                >
                    <IconContext.Provider value={{className: "info-circle"}}>
                    <CiCircleInfo style={ {color: "white", }}/>
                    </IconContext.Provider>
                </button>
                </div>
                {fgLoading ? (
                    <p>Loading...</p>
                ) : fearGreedData ? (
                    <div className="fear-greed-container">
                        {/* Horizontal bar with a pointer */}
                        <div className="fear-greed-bar">
                            <div
                                className="fear-greed-pointer"
                                style={{left: `${fearGreedValue}%`}}
                            />
                        </div>
                        <p className="fear-greed-label">
                            {fearGreedData.value} - {fearGreedData.name}
                        </p>
                        <div className="fg-sparkline">
                            {fgTrendline.length > 0 ? (
                                <Sparklines data={fgTrendline} margin={6}>
                                    <SparklinesLine style={{fill: "none"}} color="lightblue"/>
                                </Sparklines>
                            ) : (
                                <p>No historical trend data available</p>
                            )}
                        </div>
                    </div>
                ) : (
                    <p>Error loading Fear vs Greed data</p>
                )}
            </div>
            <div className="card">
                <h2>Social Signals</h2>
                <p>0</p>
            </div>
        </div>
    </section>
  );
};

export default HeroSection;
