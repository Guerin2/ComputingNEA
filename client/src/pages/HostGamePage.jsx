import React, { useState, useEffect } from 'react'
import httpClient from "../httpClient";
import { useParams } from 'react-router-dom';

const HostGamePage = () =>{
    const {roomCode} = useParams()
    const[number,setNumber] = useState("")
    const[winner,setWinner]= useState("")
    
    const callNumber = async()=>{
        const resp = await httpClient.post("//localhost:5000/host/game/"+roomCode+"/call")
        setNumber(resp.data)
    }

    const endGame = async()=>{
        const resp = await httpClient.post("//localhost:5000/host/game/"+roomCode+"/endGame") //We are in the end game now
        window.location.assign("/")
    }

    const checkWinner = async()=>{
        const resp = await httpClient.post("//localhost:5000/"+roomCode+"/checkWinner")
        setWinner(resp.data["winner"])
    }

    const defaultWinner= async()=>{
        const resp = await httpClient.post("//localhost:5000/"+roomCode+"/backToGame")
        setWinner('')
    }

    return(
        (winner == '') ? (
        <div>
            
            <h1>HOST GAME</h1>
            <h1>Game ID: {roomCode}</h1>
            <h3>Number:{number} </h3>
            <button type = "button" onClick={()=>callNumber()}>
                    Call Number
            </button>
            <button type = "button" onClick={()=>endGame()} color ="red">
                    End Game
            </button>
            <button onClick={()=>checkWinner()}>
                Check Bingos
            </button>
            <h1>{winner}</h1>
        </div>):(
            <div>
                <h1>{winner} wins</h1>
                <button onClick = {()=>defaultWinner()}> Back to game</button>
            </div>
        )
    )
}
export default HostGamePage