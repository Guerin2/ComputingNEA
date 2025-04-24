import React, { useState, useEffect } from 'react'
import httpClient from "../httpClient";
import { useParams } from 'react-router-dom';
import apiRoute from "../flaskroute"

const ClubsPage = () =>{
    const[name,setId] = useState("")
    const[password,setPassword]= useState("")
    const[clubNames,setClubNames] = useState()
    const[respStatus, setRespStatus] = useState();

    const[makeName,setMakeName] = useState("")
    const[makeDesc,setMakeDesc]= useState("")
    const[makePassword,setMakePassword]= useState("")

    let createClub = async ()=>{
                try{
                    const resp = await httpClient.post(apiRoute+"createClub", {
                        "clubName":makeName,
                        "clubDesc":makeDesc,
                        "password":makePassword
                    });
        
                    if (resp.status ==200){
                        window.location.assign("/clubs")
                    }
        
                    console.log(resp.data);
                } catch(error){
                    alert(error)
                } 
            };





    let joinClub = async ()=>{
            try{
                const resp = await httpClient.post(apiRoute+"joinClub", {
                    "clubId":name,
                    "password":password
                });
    
                if (resp.status ===200){
                    window.location.assign("/clubs")
                }
    
                console.log(resp.data);
            } catch(error){
                alert(error)
            } 
        };


    const gotoClub = async(arg) =>{
        window.location.assign("/clubs/"+arg)
    }

    const goHome = async()=>{
        window.location.assign("/")
    }


    useEffect(() => {
                (async () =>{
                    const resp = await httpClient.post(apiRoute+"getClubs")
                    console.log(resp.status)
                    setClubNames(resp.data["Clubs"])
                    setRespStatus(resp.status)
                    }
                )()
            },[])



    return(
        <div>
        {( respStatus === 200)?(
        <div>
            <div>
            <h1>Your Clubs</h1>
            {clubNames.map(value =>(
                    <button key = {value[1]} name={value[1]}  onClick = {()=>gotoClub(value[1])} >
                        {value[0]}
                        </button>
                ))}
            </div>

            <h1>Join Club</h1>
            <form>
                <div>
                    <label>Club Id: </label>
                    <input 
                    type="text" 
                    value={name} 
                    onChange={(e) => setId(e.target.value)} 
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
                <button type = "button" onClick={()=>joinClub()}>
                    Submit
                </button>
            </form>
            <h1>Create Club</h1>
            <form>
                <div>
                    <label>Club Name: </label>
                    <input 
                    type="text" 
                    value={makeName} 
                    onChange={(e) => setMakeName(e.target.value)} 
                    id=""/>
                </div>
                <div>
                    <label>Club Description: </label>
                    <input 
                    type="text" 
                    value={makeDesc} 
                    onChange={(e) => setMakeDesc(e.target.value)} 
                    id=""/>
                </div>
                <div>
                    <label>Password: </label>
                    <input 
                    type="password" 
                    value={makePassword} 
                    onChange={(e) => setMakePassword(e.target.value)} 
                    id=""/>
                </div>
                <button type = "button" onClick={()=>createClub()}>
                    Submit
                </button>
            </form>
            <button onClick={()=>goHome()}>Home</button>
        </div>
    ):(
        <div>
            <h1>Error</h1>
        </div>
    )
    }
    </div>
)}
export default ClubsPage