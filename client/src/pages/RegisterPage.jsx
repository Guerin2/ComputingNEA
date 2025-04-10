import React, {useState} from "react";
import httpClient from "../httpClient";

const RegisterPage = () =>{
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [userName, setUserName] = useState("");

    let registerUser = async ()=>{
        try{
            const resp = await httpClient.post("//localhost:5000/register", {
                email,
                password,
                userName,
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
            <h1>Create Account</h1>
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
                    <label>User Name: </label>
                    <input 
                    type="text" 
                    value={userName} 
                    onChange={(e) => setUserName(e.target.value)} 
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
                <button type = "button" onClick={()=>registerUser()}>
                    Submit
                </button>
            </form>
        </div>
    )
}

export default RegisterPage