using JSON
using PGFPlotsX
using PyCall
include("parameters.jl")

function read_calcfile(dir::String)
    json_data = JSON.parsefile(dir)
    return json_data
end

function update_parameters(params::Dict, key, value)
    if haskey(params, key)
        params[key] = value
    else
        error("$key does not exist in parameters!")
    end
end

function plot_params(params::Dict)
    for (key,value) in default_params
        if !haskey(params,key)
            params[key] = value
        end
    end
    if params["initial_band"] == 1
        println("The number of initial band can't be equal to 1, this parameter will be changed to 2! ")
        params["initial_band"] = 2

    elseif params["initial_band"] == params["final_band"]
        println("The number of bands are equal!....")
        println("Therefore we plot the number of ini_band + 1, check this in your parameters!")
        params["final_band"] = params["inital_band"] + 1

    elseif params["final_band"] < params["initial_band"]
        println("The number of final band to plot is less than initial bands!...")
        println("The end band parameter is now ini_band +1!")
        params["final_band"] = params["inital_band"] + 1
    end
    return params
end


