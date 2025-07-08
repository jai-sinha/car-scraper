import { createContext, useContext, useState, useEffect } from "react";

const LoginStatusContext = createContext();

export function useLoginStatus() {
    return useContext(LoginStatusContext);
}

export function LoginStatusProvider({ children }) {
    const storedLoginStatus = sessionStorage.getItem("loginStatus");
    const [loginStatus, setLoginStatus] = useState(
        storedLoginStatus ? JSON.parse(storedLoginStatus) : null
    );
    const [showLoginModal, setShowLoginModal] = useState(false);
    const [showLogoutModal, setShowLogoutModal] = useState(false);

    useEffect(() => {
        if (loginStatus) {
            sessionStorage.setItem("loginStatus", JSON.stringify(loginStatus));
        } else {
            sessionStorage.removeItem("loginStatus");
        }
    }, [loginStatus]);

    return (
        <LoginStatusContext.Provider value={{
            loginStatus, setLoginStatus,
            showLoginModal, setShowLoginModal,
            showLogoutModal, setShowLogoutModal
        }}>
            {children}
        </LoginStatusContext.Provider>
    );
}

export default LoginStatusContext;