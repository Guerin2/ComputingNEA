import React, {useState} from "react";
import httpClient from "../httpClient";
import apiRoute from "../flaskroute"

const LoginPage = () =>{
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    let logInUser = async ()=>{
        console.log(email,password);
        try{
            const resp = await httpClient.post(apiRoute+"login", {
                email,
                password,
            });

            if (resp.status ==200){
                window.location.assign("/")
            }

            console.log(resp.data);
        } catch(error){
            alert(error)
        } 
    };

    return(
        <div>
            <h1>Log Into Account</h1>
            <form>
                <div>
                    <label>Email: </label>
                    <input 
                    type="text" 
                    value={email} 
                    onChange={(e) => setEmail(e.target.value)} 
                    id=""/>
                </div>
                <div>
                    <label>Password: </label>
                    <input 
                    type="password" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)} 
                    id=""/>
                </div>
                <button type = "button" onClick={()=>logInUser()}>
                    Submit
                </button>
            </form>
        </div>
    )
}

export default LoginPage