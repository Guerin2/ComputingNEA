import React, { useState, useEffect } from 'react'
import httpClient from "../httpClient";
import { useParams } from 'react-router-dom';
import apiRoute from "../flaskroute"
import './navbar.css'

const Navbar =()=>{
    return(
        <nav className="navbar">
            <div className='navbar-div'>
                <ul className='link'>
                    <li>
                        <a className = 'theLink'href="/">Home</a>
                    </li>
                </ul>
            </div>
        </nav>
    )
}

export default Navbar