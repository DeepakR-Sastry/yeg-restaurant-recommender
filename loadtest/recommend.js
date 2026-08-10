import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    steady: {
      executor: 'constant-arrival-rate',
      rate: 1600,
      timeUnit: '1s',
      duration: '60s',
      preAllocatedVUs: 100,
      maxVUs: 500,
    },
  },
  summaryTrendStats: ['med', 'p(99)', 'p(99.9)', 'max'],
};

const LAT_MIN = 53.40, LAT_MAX = 53.65;
const LON_MIN = -113.70, LON_MAX = -113.30;

function uniform(min, max) {
  return min + Math.random() * (max - min);
}

export default function () {
  const payload = JSON.stringify({
    lat: uniform(LAT_MIN, LAT_MAX),
    lon: uniform(LON_MIN, LON_MAX),
    radius_m: 1000,
    k: 10,
  });

  const res = http.post('http://localhost:8000/recommend', payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  check(res, { 'status 200': (r) => r.status === 200 });
}