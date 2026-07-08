import { useNavigate } from "react-router-dom";

function logout() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
}

export default function LogoutButton() {
  const navigate = useNavigate();

  function handleClick() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <button onClick={handleClick}>
      Logout
    </button>
  );
}
