import React, { useState, useEffect } from 'react'
import httpClient from "../httpClient";
import { useParams } from 'react-router-dom';
import apiRoute from "../flaskroute"


const ClubPage = () =>{

    const {clubId} = useParams()
    const[respStatus, setRespStatus] = useState();
    const[Leaderboard,setLeaderboard] = useState();
    const[clubName,setClubName]= useState("");
    const[clubDesc,setClubDesc] = useState("")

    useEffect(() => {
                (async () =>{
                    const resp = await httpClient.post(apiRoute+"clubLeaderboard/"+clubId)
                    console.log(resp.status)
                    setLeaderboard(resp.data["Leaderboard"])
                    setClubName(resp.data["Name"])
                    setClubDesc(resp.data["Desc"])

                    setRespStatus(resp.status)
                    }
                )()
            },[])



    return(
        <div>
        {( respStatus === 200)?(
        <div>
            <div>
            <h1>{clubName} </h1>
            <h2>{clubDesc}</h2>
            {Leaderboard.map(value =>(
                    <h3 key = {value[1]} name={value[1]}  >
                        {value[0]}: {value[1]}
                        </h3>
                ))}
            </div>
        </div>
    ):(
        <div>
            <h1>Error</h1>
        </div>
    )
    }
    </div>
)}
export default ClubPage