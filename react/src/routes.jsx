import { Navigate, Outlet } from "react-router-dom";


export function LoginRequiredRoute() {
  const token = localStorage.getItem("access");

  return token ? <Outlet /> : <Navigate to="/login" replace />;
}


export function PublicRoute() {
  const token = localStorage.getItem("access");

  return token ? <Navigate to="/" replace /> : <Outlet />;
}