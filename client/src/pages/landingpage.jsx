import React , {useState, useEffect} from 'react';
import User from "../types";
import httpClient from '../httpClient';
import apiRoute from "../flaskroute"

const LandingPage= () =>{
    const [user,setUser] = useState(User || null)
    const [target,setTarget] = useState("")
    const logoutUser = async()=>{
        const resp = await httpClient.post(apiRoute+"logout")
        window.location.assign("/")
    }

    const hostGame = async()=>{
        const resp = await httpClient.get(apiRoute+"host/makeRoomCode")
        window.location.assign("/host/lobby/"+resp.data.roomCode)
    }

    const joinGame = async()=>{
        window.location.assign("/player/lobby/"+target)
    }


    const viewClubs = async()=>{
        window.location.assign("/Clubs")
    }

    useEffect(() => {
        (async () =>{
            try{
                const resp = await httpClient.get(apiRoute+"@me")
            setUser(resp.data)
            }catch(error){
                console.log("Not authed")
                setUser(null)
            }
        })()
    },[])

    return(
    <div>
        <h1>Welcome to Local Bingo</h1>
        {(user != null) ? (
            <div>
                <h2>Welcome {user.userName}</h2>
                <h3> Email: {user.email}</h3>
                <h3>ID: {user.id}</h3>
                
                <button onClick={hostGame}>Host Game</button>
                <button onClick={viewClubs}>View Clubs</button>
                <button onClick={logoutUser}>Logout</button>
                
                <form>
                <div>
                    <label>Room Code: </label>
                    <input 
                    type="text" 
                    value={target} 
                    onChange={(e) => setTarget(e.target.value)} 
                    id=""/>
                    <button type = "button" onClick={()=>joinGame()}>
                    Go
                </button>
                </div>
                </form>
                
            
            </div>
        ) : (
        <div>
            <p1>You are not logged in</p1>
            <div>
                <a href="/login"><button>Login</button></a>
                <a href="/register"><button>Register</button></a>
            </div>
        </div>
        )}
    </div>
    
    );
};

export default LandingPage;