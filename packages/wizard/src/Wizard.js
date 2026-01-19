import React, { useState } from "react";
import { useComponents, withWQ } from "@wq/react";
import { WizardContext } from "./hooks";
import * as components from "./components";

const WizardDefaults = {
    components: { ...components },
};

function Wizard({
    apiUrl,
    returnPath,
    step: externalStep,
    onSetStep,
    defaultStep = "start",
}) {
    const [taskId, setTaskId] = useState(),
        [localStep, setLocalStep] = useState(),
        [step, setStep] =
            externalStep || onSetStep
                ? [externalStep || defaultStep, onSetStep]
                : [localStep || defaultStep, setLocalStep],
        steps = useComponents(),
        Step = steps[`wizard-${step}`] || steps["wizard-unknown"];

    return (
        <WizardContext.Provider
            value={{
                apiUrl,
                returnPath,
                step,
                setStep,
                taskId,
                setTaskId,
            }}
        >
            <Step />
        </WizardContext.Provider>
    );
}

export default withWQ(Wizard, {
    defaults: WizardDefaults,
});
