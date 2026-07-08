// frontend/src/main.jsx
import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import {LoginRequiredRoute, PublicRoute} from "./routes"

import LoginPage from "./user/login";
import RegisterPage from "./user/register";
import DashboardPage from "./herd/pages/dashboard"; 
import FarmOverviewPage from "./herd/pages/farm_overview"; 
import HerdManagementPage from "./herd/pages/herd_management"; 
import PastureManagementPage from "./herd/pages/pasture_management"; 
import WeighAnimalPage from "./herd/pages/weigh_animal"; 

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route element={<PublicRoute />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        <Route element={<LoginRequiredRoute />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/farms/:farmId" element={<FarmOverviewPage />} />
          <Route path="/farms/:farmId/herds/:herdId" element={<HerdManagementPage />}/>
          <Route path="/farms/:farmId/pastures/:pastureId" element={<PastureManagementPage />}/>
          <Route path="/farms/:farmId/new-measurement/" element={<WeighAnimalPage />}/>
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

createRoot(document.getElementById("root")).render(<App />);