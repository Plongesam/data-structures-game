import React, { Component } from "react";

// renders a single worker ant
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

    render() {
        return (
            <button style={{width:"400px", height:"300px", backgroundColor:"#5f5449", border:"5px solid #5f5449", marginRight:"200px", borderRadius:"50px" }}
                onMouseEnter={this.showFood} onMouseLeave={this.hideFood}>
                {this.state.showFood &&
                    <div style={{width:"390px", height:"290px", background:"white", opacity:".2", border:"5px solid transparent", marginRight:"200px", borderRadius:"50px"}}>
                        Showing Food
                     </div>}

            </button>
        );
    }
}
export default ChamberComponent;