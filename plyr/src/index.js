import React, {useEffect} from "react";
import ReactDOM from "react-dom/client";
import Plyr from "plyr";

import "plyr/dist/plyr.css";

const Index = () => {

    useEffect(() => {
        new Plyr("#player", {
            previewThumbnails: {
                enabled: true,
                src: "/stc/thumbnails.vtt",
            }
        });
    }, [])

    return (
        <video id="player" controls>
            <source src="/stc/valerian-1080p.mp4" type="video/mp4"/>
        </video>
    )
}

const root = document.getElementById("root");
ReactDOM.createRoot(root).render(<Index/>);
