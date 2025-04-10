import React, { useState, useEffect } from 'react'
import httpClient from "../httpClient";
import { data, useParams } from 'react-router-dom';
import './card.css'

<link rel="stylesheet" href = "card.css"/>


var buttonStates = [false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false]



function parseBingoString(bingoString) {
    const arr1 = bingoString.split('|').map(item => item.trim())
    const hold = [[],[],[]]
    const ret = []
    for (let i=0;i<27;i++){
        hold[i%3].push(arr1[i])
    }
    var i=0
    hold.forEach(element => {
        
        element.forEach(val =>{
            ret.push([val,i])
            if (val == 0){
             buttonStates[i] = true   
            }
            i++
            
        })
        
    });
    return ret
}


const PlayerPageLobby = () =>{


    const [respStatus, setRespStatus] = useState();
    const [card,setCard] = useState();
    const [selected,seSelected] = useState("") 
      
    const {roomCode} = useParams()


    const changeButtonStates = (i)=>{
        seSelected(Math.random()) // idfk
        buttonStates[i] = !buttonStates[i]
    }

    let bingoCheck = async()=>{
        const response = await httpClient.post("//localhost:5000/"+roomCode+"/checkBingo",{
            "states":buttonStates
        })
    }

    



    useEffect(() => {
            (async () =>{
                const resp = await httpClient.post("//localhost:5000/player/game/"+roomCode)
                console.log(resp.status)
                setRespStatus(resp.status)
                setCard(parseBingoString(resp.data.card))
                }
            )()
        },[])


    
    return(
    <div>
        {( String(respStatus) == "200")?(
        <div>
            <h1>You Are In The Game</h1>
            <h1>Game ID: {roomCode}</h1>

            
            <div className="container">
                {card.map(value =>(
                    <button key = {value[1]} name={value[1]} disabled = {(value[0] == 0)} onClick = {()=>changeButtonStates(value[1])} className={`${buttonStates[value[1]] ? "c1" : "c2"}`}>
                        {(String(value[0]) === "0")?(" "):(value[0])}
                        </button>
                ))}
            </div>
            <div>
                <button onClick={()=>bingoCheck()}>
                    BINGO
                </button>
            </div>
            
        </div>
        ):(
            <div>
                <h1>Game Doesnt Exist</h1>
            </div>
        )
        }
        </div>
    )
}

export default PlayerPageLobby