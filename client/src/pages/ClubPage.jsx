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
    const[owner,setOwner] = useState(Boolean)
    const[kickId,setKickId]=useState("")
    const[popUp,setPopUp] = useState("")

    const kickFromClub = async(id)=>{

        try {
            httpClient.post(apiRoute+"kickFromClub",{
                "userId": id,
                "clubId":clubId
            })
        }catch(error){
            alert(error)
        }
    }

    const deleteClub = async(id)=>{

        try {
            const resp = await httpClient.post(apiRoute+"deleteClub",{
                "clubId":clubId
            })
            window.location.assign("/clubs")
        }catch(error){
            alert(error)
        }
    }




    useEffect(() => {
                (async () =>{
                    const resp = await httpClient.post(apiRoute+"clubLeaderboard/"+clubId)
                    console.log(resp.status)
                    setLeaderboard(resp.data["Leaderboard"])
                    setClubName(resp.data["Name"])
                    setClubDesc(resp.data["Desc"])
                    setOwner(resp.data["Perms"])
                    setRespStatus(resp.status)
                    }
                )()
            },[])



    return(
        <div>
        {( respStatus === 200)?(
        <div>
            <h1>{clubName} </h1>
            <h2>Club Id: {clubId}</h2>
            <h2>{clubDesc}</h2>
            {Leaderboard.map(value =>(
                <div>
                    <h3 key = {value[2]} name={value[1]} >{value[0]}: {value[1]}</h3>
                        {(owner)?(
                            <div>
                                <button key = {value[2]} name={value[1]} onClick={()=>kickFromClub(value[2])} >
                            Kick
                                </button>
                            </div>
                        ):(<div></div>)}
                </div>
            ))}
            {(owner)?(
                <button onClick={()=>deleteClub()}>Delete Club</button>
            ):(<div></div>)}
        </div>
    ):(
        <div>
            <h1>Error</h1>
        </div>
    )
    }
</div>
)
}
export default ClubPage