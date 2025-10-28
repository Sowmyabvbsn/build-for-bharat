import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";

const LandingPage = () => {
  const navigate = useNavigate();
  const [districts, setDistricts] = useState([]);
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [locationLoading, setLocationLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRegion, setSelectedRegion] = useState("All");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [districtsRes, overviewRes] = await Promise.all([
        axios.get(`${API}/districts`),
        axios.get(`${API}/state/overview`)
      ]);
      
      setDistricts(districtsRes.data);
      setOverview(overviewRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const detectLocation = () => {
    if (!navigator.geolocation) {
      alert("आपका ब्राउज़र लोकेशन सपोर्ट नहीं करता / Your browser doesn't support geolocation");
      return;
    }

    setLocationLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const response = await axios.post(`${API}/location/detect`, {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });

          if (response.data.success) {
            navigate(`/district/${response.data.district.code}`);
          } else {
            alert("जिला नहीं मिला। कृपया मैन्युअल रूप से चुनें / District not found. Please select manually");
          }
        } catch (error) {
          console.error("Location detection error:", error);
          alert("लोकेशन पता नहीं लगा सके / Could not detect location");
        } finally {
          setLocationLoading(false);
        }
      },
      (error) => {
        console.error("Geolocation error:", error);
        alert("लोकेशन एक्सेस अस्वीकृत / Location access denied");
        setLocationLoading(false);
      }
    );
  };

  const filteredDistricts = districts.filter((d) => {
    const matchesSearch = d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         d.name_hi.includes(searchTerm);
    const matchesRegion = selectedRegion === "All" || d.region === selectedRegion;
    return matchesSearch && matchesRegion;
  });

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>डेटा लोड हो रहा है... / Loading data...</p>
      </div>
    );
  }

  return (
    <div className="landing-container">
      <div className="landing-header">
        <h1 className="landing-title" data-testid="main-title">मनरेगा - हमारी आवाज़, हमारे अधिकार</h1>
        <h2 className="landing-title-hindi hindi-text">MGNREGA - Our Voice, Our Rights</h2>
        <p className="landing-subtitle">उत्तर प्रदेश | Uttar Pradesh</p>
      </div>

      {overview && (
        <div className="state-overview">
          <h2 className="overview-title" data-testid="overview-title">राज्य का प्रदर्शन / State Overview</h2>
          
          <div className="stats-grid">
            <div className="stat-card" data-testid="total-districts-card">
              <div className="stat-icon">🏛️</div>
              <div className="stat-value">{overview.total_districts}</div>
              <div className="stat-label">जिले / Districts</div>
            </div>

            <div className="stat-card" data-testid="total-workers-card">
              <div className="stat-icon">👷</div>
              <div className="stat-value">{(overview.total_active_workers / 100000).toFixed(1)}L</div>
              <div className="stat-label">सक्रिय कार्यकर्ता / Active Workers</div>
            </div>

            <div className="stat-card" data-testid="person-days-card">
              <div className="stat-icon">📊</div>
              <div className="stat-value">{(overview.total_person_days / 10000000).toFixed(1)}Cr</div>
              <div className="stat-label">व्यक्ति दिवस / Person Days</div>
            </div>

            <div className="stat-card" data-testid="expenditure-card">
              <div className="stat-icon">💰</div>
              <div className="stat-value">₹{overview.total_expenditure_crores.toFixed(0)}</div>
              <div className="stat-label">करोड़ खर्च / Crores Spent</div>
            </div>
          </div>
        </div>
      )}

      <div className="location-section">
        <h3 style={{marginBottom: '1rem', fontSize: '1.3rem', color: '#2d3748'}}>
          अपने जिले का डेटा देखें / View Your District Data
        </h3>
        <button 
          className="location-button" 
          onClick={detectLocation}
          disabled={locationLoading}
          data-testid="detect-location-btn"
        >
          {locationLoading ? "पता लगा रहे हैं... / Detecting..." : "📍 मेरा जिला खोजें / Find My District"}
        </button>
      </div>

      <div style={{background: 'white', borderRadius: '20px', padding: '2rem', marginTop: '2rem'}}>
        <h2 className="overview-title">जिला चुनें / Select District</h2>
        
        <div style={{marginBottom: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center'}}>
          <input
            type="text"
            placeholder="जिला खोजें / Search district..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            data-testid="district-search-input"
            style={{
              padding: '0.8rem 1.5rem',
              fontSize: '1rem',
              borderRadius: '50px',
              border: '2px solid #e2e8f0',
              width: '300px',
              outline: 'none'
            }}
          />
          
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            data-testid="region-filter-select"
            style={{
              padding: '0.8rem 1.5rem',
              fontSize: '1rem',
              borderRadius: '50px',
              border: '2px solid #e2e8f0',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            <option value="All">सभी क्षेत्र / All Regions</option>
            <option value="North">उत्तर / North</option>
            <option value="South">दक्षिण / South</option>
            <option value="East">पूर्व / East</option>
            <option value="West">पश्चिम / West</option>
            <option value="Central">मध्य / Central</option>
          </select>
        </div>

        <div className="district-grid">
          {filteredDistricts.map((district) => (
            <div
              key={district.code}
              className="district-card"
              onClick={() => navigate(`/district/${district.code}`)}
              data-testid={`district-card-${district.code}`}
            >
              <div className="district-name">{district.name}</div>
              <div className="district-name-hindi hindi-text">{district.name_hi}</div>
              <span className="district-region">{district.region}</span>
            </div>
          ))}
        </div>

        {filteredDistricts.length === 0 && (
          <p style={{textAlign: 'center', padding: '2rem', color: '#718096'}}>
            कोई जिला नहीं मिला / No districts found
          </p>
        )}
      </div>
    </div>
  );
};

export default LandingPage;
