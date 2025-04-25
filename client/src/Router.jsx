import {BrowserRouter, Route, Routes, useParams} from 'react-router-dom'
import LandingPage from './pages/landingpage'
import React from 'react'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import HostPageLobby from './pages/HostPageLobby'
import PlayerPageLobby from './pages/PlayerPageLobby'
import HostGamePage from './pages/HostGamePage'
import ClubsPage from './pages/ClubsPage'
import ClubPage from './pages/ClubPage'
import NotFound from './pages/NotFound'
import Navbar from './pages/navbar'




const Router = () =>{
    return(
        <BrowserRouter>
            <Navbar/>
            <Routes>
                <Route path="/" exact element={<LandingPage/>}/>
                <Route path="/login" exact element={<LoginPage/>}/>
                <Route path="/register" exact element={<RegisterPage/>}/>
                <Route path="/host/lobby/:roomCode" exact element={<HostPageLobby/>}/>
                <Route path="/player/lobby/:roomCode" exact element={<PlayerPageLobby/>}/>
                <Route path="/host/game/:roomCode" exact element={<HostGamePage/>}/>
                <Route path="/clubs" exact element={<ClubsPage/>}/>
                <Route path="/clubs/:clubId" exact element={<ClubPage/>}/>
                <Route exact element = {<NotFound/>}/>
            </Routes>
        </BrowserRouter>
    );
};

export default Router;