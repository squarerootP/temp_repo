import searchIcon from '@/assets/images/icons/search_icon.png';

function SearchBar() {
    return (
        <div className="w-max h-14 rounded-lg flex flex-row items-center space-x-2">
            <input 
                type="text" 
                placeholder="Search for books, authors, genres..."  
                className="outline-none w-96 h-full border-black border-2 rounded-2xl px-4 bg-green-300 placeholder-black"
            />
            <button className="border-black border-2 rounded-2xl flex h-full w-14 items-center justify-between bg-green-300"  
            >
                <img src={searchIcon} alt="search_icon" className="h-12 w-12 p-2" />
            </button>
        </div>
    )
}

export default SearchBar