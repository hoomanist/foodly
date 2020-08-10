import React from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';


class Main extends React.Component {
  render(){
    return(
      <p>سلام فودلی</p>
    )
  }
}

class Header extends React.Component{
  render(){
    return (
      <nav class="navbar navbar-dark bg-dark">
        <a class="navbar-brand" href="/#">
            فودلی - شبکه اجتماعی برای غذاها
        </a>
      </nav>
    );
  }
}

function App() {

  return (
    <div className="App">
      <Header/>
      <Main/>
    </div>
  );
}

export default App;
