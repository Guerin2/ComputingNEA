import React, { useState, useEffect } from 'react'
import httpClient from "../httpClient";
import { useParams } from 'react-router-dom';
import apiRoute from "../flaskroute"

const HostGamePage = () =>{
    
    const {roomCode} = useParams()
    const[numbers,setNumbers] = useState("")
    const[winner,setWinner]= useState("")
    const[perm,setPerm] = useState("")
    const[leaderboard,setLeaderboard] = useState()
    
    
    const callNumber = async()=>{
        const resp = await httpClient.post(apiRoute+"host/game/"+roomCode+"/call")
        setNumbers(resp.data["numbers"])
        setLeaderboard(resp.data["leaderboard"])
    }

    const endGame = async()=>{
        const resp = await httpClient.post(apiRoute+"host/game/"+roomCode+"/endGame") //We are in the end game now
        window.location.assign("/")
    }

    const checkWinner = async()=>{
        const resp = await httpClient.post(apiRoute+roomCode+"/checkWinner")
        setWinner(resp.data["winner"])
    }

    const defaultWinner= async()=>{
        const resp = await httpClient.post(apiRoute+roomCode+"/backToGame")
        setWinner('')
    }


    useEffect(() => {
            (async () =>{
                const resp = await httpClient.post(apiRoute+"host/game/"+roomCode+"/checkHost")
                if (resp.status != 200){
                    window.location.assign("/")
                }
            })()
        },[])



    return(
        (winner == '') ? (
        <div>
            
            <h1>HOST GAME</h1>
            <h1>Game ID: {roomCode}</h1>
            <h1>Number:{numbers[0]} </h1>
            <h2>Previous Numbers: {numbers[1]} {numbers[2]} {numbers[3]} {numbers[4]}</h2>
            <button type = "button" onClick={()=>callNumber()}>
                    Call Number
            </button>
            <button type = "button" onClick={()=>endGame()} color ="red">
                    End Game
            </button>
            <button onClick={()=>checkWinner()}>
                Check Bingos
            </button>
            <div>
                <h2>Leaderboard</h2>
                <ul>{leaderboard?.map(value => <h3 key={value[0]}>{value[0]} : {value[1]}</h3>)}</ul>     
            </div>
            
        </div>):(
            <div>
                <h1>{winner} wins</h1>
                <button onClick = {()=>defaultWinner()}> Back to game</button>
            </div>
        )
    )
}
export default HostGamePage