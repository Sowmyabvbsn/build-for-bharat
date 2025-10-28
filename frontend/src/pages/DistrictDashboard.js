import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

const DistrictDashboard = () => {
  const { code } = useParams();
  const navigate = useNavigate();
  const [currentData, setCurrentData] = useState(null);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDistrictData();
  }, [code]);

  const fetchDistrictData = async () => {
    try {
      setLoading(true);
      const [currentRes, trendsRes] = await Promise.all([
        axios.get(`${API}/districts/${code}/current`),
        axios.get(`${API}/districts/${code}/trends?months=6`)
      ]);
      
      setCurrentData(currentRes.data);
      setTrends(trendsRes.data.trends);
    } catch (error) {
      console.error("Error fetching district data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>डेटा लोड हो रहा है... / Loading data...</p>
      </div>
    );
  }

  if (!currentData) {
    return (
      <div className="error-message">
        डेटा नहीं मिला / Data not found
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <button className="back-button" onClick={() => navigate("/")} data-testid="back-button">
          ← वापस जाएं / Go Back
        </button>
        
        <h1 className="district-title" data-testid="district-title">{currentData.district_name}</h1>
        <p className="district-title-hindi hindi-text">
          {currentData.month} का प्रदर्शन / Performance for {currentData.month}
        </p>
        
        <div style={{marginTop: '1rem'}}>
          <span className={`performance-badge grade-${currentData.performance_grade}`} data-testid="performance-badge">
            ग्रेड / Grade: {currentData.performance_grade} ({currentData.performance_score.toFixed(0)}/100)
          </span>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-card primary" data-testid="job-cards-metric">
          <div className="metric-header">
            <span className="metric-icon">📋</span>
            <div>
              <div className="metric-label">जॉब कार्ड / Job Cards</div>
              <div className="metric-value">{(currentData.job_cards_issued / 100000).toFixed(1)}L</div>
            </div>
          </div>
          <div className="metric-subtext">जारी किए गए / Issued</div>
        </div>

        <div className="metric-card success" data-testid="active-workers-metric">
          <div className="metric-header">
            <span className="metric-icon">👷</span>
            <div>
              <div className="metric-label">सक्रिय कार्यकर्ता / Active Workers</div>
              <div className="metric-value">{(currentData.active_workers / 1000).toFixed(1)}K</div>
            </div>
          </div>
          <div className="metric-subtext">कार्यरत / Working</div>
        </div>

        <div className="metric-card info" data-testid="person-days-metric">
          <div className="metric-header">
            <span className="metric-icon">📊</span>
            <div>
              <div className="metric-label">व्यक्ति दिवस / Person Days</div>
              <div className="metric-value">{(currentData.person_days_generated / 100000).toFixed(1)}L</div>
            </div>
          </div>
          <div className="metric-subtext">उत्पन्न / Generated</div>
        </div>

        <div className="metric-card warning" data-testid="avg-days-metric">
          <div className="metric-header">
            <span className="metric-icon">📅</span>
            <div>
              <div className="metric-label">औसत दिन / Average Days</div>
              <div className="metric-value">{currentData.average_days_per_household}</div>
            </div>
          </div>
          <div className="metric-subtext">प्रति परिवार / Per Household</div>
        </div>

        <div className="metric-card primary" data-testid="works-metric">
          <div className="metric-header">
            <span className="metric-icon">🏗️</span>
            <div>
              <div className="metric-label">कार्य / Works</div>
              <div className="metric-value">{currentData.works_completed}</div>
            </div>
          </div>
          <div className="metric-subtext">
            पूर्ण / Completed | चालू / Ongoing: {currentData.works_ongoing}
          </div>
        </div>

        <div className="metric-card success" data-testid="expenditure-metric">
          <div className="metric-header">
            <span className="metric-icon">💰</span>
            <div>
              <div className="metric-label">व्यय / Expenditure</div>
              <div className="metric-value">₹{currentData.expenditure_crores}</div>
            </div>
          </div>
          <div className="metric-subtext">करोड़ / Crores</div>
        </div>

        <div className="metric-card info" data-testid="women-participation-metric">
          <div className="metric-header">
            <span className="metric-icon">👩</span>
            <div>
              <div className="metric-label">महिला भागीदारी / Women</div>
              <div className="metric-value">{currentData.women_participation_percent}%</div>
            </div>
          </div>
          <div className="metric-subtext">भागीदारी / Participation</div>
        </div>

        <div className="metric-card warning" data-testid="sc-st-participation-metric">
          <div className="metric-header">
            <span className="metric-icon">👥</span>
            <div>
              <div className="metric-label">SC/ST भागीदारी</div>
              <div className="metric-value">{currentData.sc_st_participation_percent}%</div>
            </div>
          </div>
          <div className="metric-subtext">भागीदारी / Participation</div>
        </div>
      </div>

      {trends.length > 0 && (
        <div className="trends-section">
          <h2 className="section-title">पिछले 6 महीने का रुझान / Last 6 Months Trend</h2>
          
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="person_days"
                  stroke="#667eea"
                  strokeWidth={3}
                  name="Person Days"
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="active_workers"
                  stroke="#38ef7d"
                  strokeWidth={3}
                  name="Active Workers"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-container" style={{marginTop: '2rem'}}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="performance_score" fill="#667eea" name="Performance Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div style={{textAlign: 'center', marginTop: '2rem'}}>
        <button
          onClick={() => navigate('/compare')}
          data-testid="compare-districts-btn"
          style={{
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            color: 'white',
            border: 'none',
            padding: '1rem 2rem',
            fontSize: '1.1rem',
            fontWeight: '600',
            borderRadius: '50px',
            cursor: 'pointer'
          }}
        >
          जिलों की तुलना करें / Compare Districts
        </button>
      </div>
    </div>
  );
};

export default DistrictDashboard;
