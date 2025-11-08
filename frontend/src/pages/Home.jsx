import {styles} from "../styles/style_config.jsx"
import NavBar from "../components/layout/Navbar.jsx";
import Footer from "../components/layout/Footer.jsx";
import BookCard from "../components/Book/BookCard.jsx";
import Logo from "../components/common/Logo.jsx";
import "@/index.css"
import SearchBar from "../components/layout/SearchBAr.jsx";
function Home() {
  return (
    <><NavBar></NavBar>

    {/* The line that separates the nav and the main body */}
    <div className="border-2 border-white"></div>
    {/* <div className="absolute inset-0">
      <div className="bg-[url('src/assets/images/bg/home_bg_3.jpg')] bg-cover bg-center w-full h-full opacity-30 overflow-hidden"></div>
    </div> */}
    {/* First Section */}
    <div className="relative w-[calc(90vw)] min-h-screen overflow-hidden group mx-auto flex justify-center items-center space-y-28">
      <div className="absolute inset-0 bg-[url('src/assets/images/bg/home_bg_3.jpg')] bg-cover bg-center transition-transform duration-500 group-hover:scale-105"></div>

      <div className="relative z-10 flex flex-col mx-auto p-6 justify-center items-center space-y-8">
        <div className="h-8"></div>
        <Logo size={260} />
        <SearchBar />
        <h1 className="font-bold text-white text-outline text-4xl ">
          Choose what to read today
        </h1>
        <div className="h-12"></div>

        {/* This show books horizontally */}
        <div className="flex flex-row space-x-8">
          <BookCard book_title="Alice in Wonderland" summary="This story is about a girl who..." img_path="./src/assets/images/book_img/alice_in_wonderland.png"></BookCard>
          <BookCard book_title="Romeo and Juliet" summary="This book is about a couple who..." img_path="./src/assets/images/book_img/romeo_and_juliet.jpg"></BookCard>
          <BookCard book_title="Frankenstein" summary="This book is about Frank..." img_path = "./src/assets/images/book_img/frankenstein.jpg"></BookCard>
          <BookCard book_title="Price and Prejudice" summary="This book is about Price..." img_path = "./src/assets/images/book_img/price_and_prejudice.jpg"></BookCard>
          <BookCard book_title="MobyDick and the White whale" summary="This book is about the white whale..." img_path = "./src/assets/images/book_img/moby_dick.jpg"></BookCard>
        </div>
        <div className="h-40"></div>
      </div>
    </div>


    <div className="border-2 border-white"></div>

    <Footer></Footer>
  </>
  )
  
}

export default Home