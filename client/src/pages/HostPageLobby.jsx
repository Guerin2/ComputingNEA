import React, { useState, useEffect } from 'react'
import httpClient from "../httpClient";
import { useParams } from 'react-router-dom';
import apiRoute from "../flaskroute"

const HostPageLobby = () =>{
    const {roomCode} = useParams()
    const[names,setNames] = useState("")
    
    const refreshPlayers = async()=>{
        const resp = await httpClient.post(apiRoute+"host/lobby/"+roomCode+"/getPlayers")
        setNames(resp.data["names"])
    }
    const startGame = async()=>{
        const resp = await httpClient.post(apiRoute+"host/game/"+roomCode+"/begin")
        window.location.assign("/host/game/"+roomCode)
    }
    
    return(
        <div>
            <h1>Host Lobby</h1>
            <h1>Game ID: {roomCode}</h1>
            <h3>Players: {names}</h3>
            <button type = "button" onClick={()=>refreshPlayers()}>
                    Refresh Players
            </button>
            <button type = "button" onClick={()=>startGame()}>
                    Start Game
            </button>
        </div>
    )
}
export default HostPageLobby