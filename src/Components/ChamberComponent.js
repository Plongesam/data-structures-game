import React, { Component } from "react";
import Ant from './AntComponent';
import Crumb from './dsgCrumb.png';
import Donut from './dsgDonut.png';
import Sugar from './dsgSugar.png';

// renders a single chamber
class ChamberComponent extends React.Component {
    constructor(props) {
        super(props);
        this.chamberRef = React.createRef();
        this.state = ({showFood:false});
        this.showFood = this.showFood.bind(this);
        this.hideFood = this.hideFood.bind(this);
    }

  showFood() {
    this.setState({showFood: true});
  }
  hideFood(){
      this.setState({showFood:false});
  }

  // renders the ants in a chamber
  renderAnts = () => {
    var ants=[];
    for(var i = 0; i < this.props.ants; i++) {
      ants.push(<Ant/>);
    }

    return ants.map((ant) => <li style={{listStyleType:"none"}}>{ant}</li>);
  }

    render() {
        return (
            <button id='chamberButton' style={{width:"400px", height:"300px", backgroundColor:"#5f5449", border:"5px solid #5f5449", marginRight:"200px", borderRadius:"50px" }}
                onClick={this.showFood} onMouseLeave={this.hideFood} >

                <div style={{display:"flex", flexDirection:"row", alignItems:"space-around", position:'absolute', top:'190px'}}>
                    {this.renderAnts()}
                </div>
                {this.state.showFood &&
                    <div name="chamberFoodUI" style={{flexDirection:"row", fontSize:'30px', width:"390px", height:"290px", backgroundColor:"rgba(255, 255, 255, .3", border:"5px solid rgba(255, 255, 255, .2) ", marginRight:"200px", borderRadius:"45px"}}>
                        <p>total food in chamber: {this.props.food}</p>
                        <img id="crumb" src={Crumb} alt="crumb" style={{width:"100px", position:"relative", left:"15px", top:"10px"}} />
                        <img id="sugar" src={Sugar} alt="sugar" style={{width:"100px", position:"relative", left:"130px", bottom:"40px"}} />
                        <img id="donut" src={Donut} alt="donut" style={{width:"100px", position:"relative", left:"245px", bottom:"90px"}} />
                        <span style={{position:"relative", bottom:"90px"}}>{this.props.berry}</span>
                        <span style={{position:"relative", bottom:"90px", right:"120px"}}>{this.props.crumb}</span>
                        <span style={{position:"relative", bottom:"90px", left:"105px"}}>{this.props.donut}</span>
                    </div>
                }
            </button>
        );
    }
}
export default ChamberComponent;