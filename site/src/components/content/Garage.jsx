import { useLoginStatus } from "../contexts/LoginStatusContext";

function Garage() {
    const { loginStatus } = useLoginStatus();

    if (!loginStatus) {
        return <h2>You need to log in to use this feature.</h2>;
    }

    return <h1>Hello Garage</h1>;
}

export default Garage;