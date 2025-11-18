import searchIcon from '@/assets/images/icons/search_icon.png';
import React from 'react';
function SearchBar({ onSearch }) {
  const [query, setQuery] = React.useState("");

  function handleSubmit(e) {
    e.preventDefault();
    onSearch(query);  
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="w-max h-14 rounded-lg flex flex-row items-center space-x-2"
    >
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="✨ I want to find books that..."
        className="outline-none w-96 h-full border-white border-2 rounded-2xl px-4 bg-green-600 placeholder-white text-white"
      />

      <button
        type="submit"
        className="border-white border-2 rounded-2xl flex h-full w-14 items-center justify-center bg-green-600"
      >
        <img src={searchIcon} className="h-12 w-12 p-2 invert" />
      </button>
    </form>
  );
}

export default SearchBar;
