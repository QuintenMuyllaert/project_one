const delay = (ms) => {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const fetchJson = async (url) => {
    const repl = await fetch(url);
    const json = await repl.json();
    return json;
}