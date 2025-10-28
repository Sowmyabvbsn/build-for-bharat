import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const ComparePage = () => {
  const navigate = useNavigate();
  const [districts, setDistricts] = useState([]);
  const [selectedDistricts, setSelectedDistricts] = useState([]);
  const [comparisonData, setComparisonData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDistricts();
  }, []);

  const fetchDistricts = async () => {
    try {
      const response = await axios.get(`${API}/districts`);
      setDistricts(response.data);
    } catch (error) {
      console.error("Error fetching districts:", error);
    }
  };

  const handleDistrictSelect = (code) => {
    if (selectedDistricts.includes(code)) {
      setSelectedDistricts(selectedDistricts.filter((c) => c !== code));
    } else if (selectedDistricts.length < 5) {
      setSelectedDistricts([...selectedDistricts, code]);
    } else {
      alert("अधिकतम 5 जिले चुन सकते हैं / Maximum 5 districts allowed");
    }
  };

  const compareDistricts = async () => {
    if (selectedDistricts.length < 2) {
      alert("कृपया कम से कम 2 जिले चुनें / Please select at least 2 districts");
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get(`${API}/districts/compare?codes=${selectedDistricts.join(",")}`);
      setComparisonData(response.data.comparisons);
    } catch (error) {
      console.error("Error comparing districts:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="compare-container">
      <div className="dashboard-header">
        <button className="back-button" onClick={() => navigate("/")} data-testid="back-button">
          ← वापस जाएं / Go Back
        </button>
        
        <h1 className="district-title" data-testid="compare-title">जिलों की तुलना / Compare Districts</h1>
        <p className="district-title-hindi">अधिकतम 5 जिले चुनें / Select up to 5 districts</p>
      </div>

      <div style={{background: 'white', borderRadius: '20px', padding: '2rem', marginBottom: '2rem'}}>
        <div className="district-grid">
          {districts.map((district) => (
            <div
              key={district.code}
              className={`district-card ${selectedDistricts.includes(district.code) ? 'selected' : ''}`}
              onClick={() => handleDistrictSelect(district.code)}
              data-testid={`compare-district-${district.code}`}
              style={{
                border: selectedDistricts.includes(district.code) ? '3px solid #667eea' : '2px solid transparent',
                background: selectedDistricts.includes(district.code) ? '#f0f4ff' : 'white'
              }}
            >
              <div className="district-name">{district.name}</div>
              <div className="district-name-hindi hindi-text">{district.name_hi}</div>
              <span className="district-region">{district.region}</span>
              {selectedDistricts.includes(district.code) && (
                <div style={{marginTop: '0.5rem', color: '#667eea', fontWeight: 'bold'}}>✓ चयनित / Selected</div>
              )}
            </div>
          ))}
        </div>

        <div style={{textAlign: 'center', marginTop: '2rem'}}>
          <button
            onClick={compareDistricts}
            disabled={loading || selectedDistricts.length < 2}
            data-testid="compare-button"
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              padding: '1rem 2rem',
              fontSize: '1.1rem',
              fontWeight: '600',
              borderRadius: '50px',
              cursor: selectedDistricts.length < 2 ? 'not-allowed' : 'pointer',
              opacity: selectedDistricts.length < 2 ? 0.5 : 1
            }}
          >
            {loading ? "तुलना हो रही है... / Comparing..." : `तुलना करें / Compare (${selectedDistricts.length} selected)`}
          </button>
        </div>
      </div>

      {comparisonData.length > 0 && (
        <div className="trends-section">
          <h2 className="section-title">तुलना परिणाम / Comparison Results</h2>
          
          <div className="chart-container" style={{height: '400px', marginTop: '2rem'}}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="district_name" angle={-15} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="person_days_generated" fill="#667eea" name="Person Days" />
                <Bar dataKey="active_workers" fill="#38ef7d" name="Active Workers" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-container" style={{height: '400px', marginTop: '2rem'}}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="district_name" angle={-15} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="performance_score" fill="#f093fb" name="Performance Score" />
                <Bar dataKey="expenditure_crores" fill="#fbbf24" name="Expenditure (Cr)" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="compare-grid" style={{marginTop: '2rem'}}>
            {comparisonData.map((data) => (
              <div key={data.district_code} className="metric-card primary" data-testid={`comparison-card-${data.district_code}`}>
                <h3 style={{fontSize: '1.5rem', fontWeight: '700', marginBottom: '1rem'}}>
                  {data.district_name}
                </h3>
                <div style={{display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
                  <div>
                    <strong>Grade:</strong> <span className={`performance-badge grade-${data.performance_grade}`} style={{marginLeft: '0.5rem', padding: '0.3rem 0.8rem', fontSize: '0.9rem'}}>{data.performance_grade}</span>
                  </div>
                  <div><strong>Active Workers:</strong> {(data.active_workers / 1000).toFixed(1)}K</div>
                  <div><strong>Person Days:</strong> {(data.person_days_generated / 100000).toFixed(1)}L</div>
                  <div><strong>Avg Days:</strong> {data.average_days_per_household}</div>
                  <div><strong>Expenditure:</strong> ₹{data.expenditure_crores} Cr</div>
                  <div><strong>Women %:</strong> {data.women_participation_percent}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ComparePage;
