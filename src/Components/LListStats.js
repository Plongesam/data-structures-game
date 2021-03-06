import React, { Component } from "react";
import './LListGameboard.css';

// shows the in  game stats in the upper right corner of game page
class LListStats extends React.Component {
  constructor(props) {
    super(props);
    this.llistRef = React.createRef();
  }

  render() {
    return (
      <div className="stats-row">
        <div className="stats">
          <p>TIME</p>
          <p>FOOD</p>
          <p>ANTS</p>
          <p>CHAMBERS</p>
        </div>
        <div className="stats">
          <p>{this.props.time}</p>
          <p>{this.props.food}</p>
          <p>{this.props.ants}</p>
          <p>{this.props.chambers}</p>
        </div>
      </div>

    )
  }
}
export default LListStats;