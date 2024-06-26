const NEXT_PUBLIC_CHAT_API = process.env.NEXT_PUBLIC_CHAT_API;


/**
 * Handle streaming response from FASTAPI Datausa-chat API wrapper
 * @param {*} input question input
 * @param {*} handleTable function to handle table response from API
 * @param {*} updater  function to handle setMessegas
 * @param {*} setLoading function to handle loading 
 */
export default async function ReflectionWrap(input, handleTable, updater, setLoading) {
    
    const _URL = `${NEXT_PUBLIC_CHAT_API}wrap/${input}`

    try {
        const response = await fetch(_URL, {
            method: 'GET'
        });

        if(response.body){
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            while (true) {
                const {done, value} = await reader.read();
                if (done){
                    break;
                }
                const str = decoder.decode(value);
                try {
                    const jsonStr = str.replace(/^data: /, '').trim();
                    const resp = JSON.parse(jsonStr);
                    if (resp.content.length === 3 ) {
                        handleTable(resp.content[0]);
                        updater((prevMessages) => [...prevMessages, { text: resp.content[2], user: false }]);
                    } else {
                        updater((prevMessages) => [...prevMessages, { text: resp.content, user: false }]);
                    }

                } catch (error) {
                    console.error(error);
                    setLoading(false);
                } 
            }
            setLoading(false);
        }
    } catch (error) {
        console.error(error);
        setLoading(false);
    }
    

}


