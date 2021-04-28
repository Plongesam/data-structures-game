import React, { Component } from "react";
import Ant from './ant.png';

// renders a single worker ant
class AntComponent extends React.Component {
    render() {
        return (
            <img id="WorkerAnt" src={Ant} alt="worker ant" style={{width:"110px"}}/>
        );
    }
}
export default AntComponent;