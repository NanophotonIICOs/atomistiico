include("build.jl")
include("utils.jl")

function plots(dir_calc,params::Dict)
    data        = read_calcfile(dir_calc)
    np          = pyimport("numpy")
    bands       = np.array(data["energies"])
    xtickcoords = data["label_xcoords"]
    plot_title  = data["name"]
    parameters = plot_params(params)
    update_parameters(parameters,"xmin",float(xtickcoords[1]))
    update_parameters(parameters,"xmax",float(xtickcoords[end]))

    if parameters["initial_band"] > size(bands,3)
        update_parameters(parameters,"initial_band",2)
        println("The number of initial band is greath than size of bands array") 
    elseif parameters["final_band"] > size(bands,3)
        total_calc_bands = size(bands,3)
        update_parameters(parameters,"final_band",total_calc_bands)
        println("The number of final band to plots are excess of number of calculate bands!\n
                 Therefore the final band to plot is the number of total calculate bands:$(total_calc_bands)")
    end
    #fermi level coordinates
    xf =[parameters["xmin"],parameters["xmax"]]
    yf =[0,0] 
    plot = @pgf TikzPicture(
    Axis(
    { 
        height = parameters["height"],
        width  = parameters["width"],
        title  = "$(plot_title)",
        title_style ="{scale=$(parameters["ax_labels_scale"]),at={(axis description cs:0.5,1.05)}}",
        #-------------------------------------------------------------------------
        scale_only_axis   = "$(parameters["scale_only_axis"])",
        "axis background/.style={fill=none}",
        line_width        = "{$(parameters["ax_lw"])}",
        tick_style        = "{line width=$(parameters["ax_lw"]),black}",
        ticklabel_style   = "{scale=$(parameters["ax_tick_scale"])}",
        major_tick_length = "{$(parameters["ax_size_major_tick"])}",
        minor_tick_length = "{$(parameters["ax_size_minor_tick"])}",
        ylabel_style      = "{scale=$(parameters["ax_labels_scale"])}",
        # "every tick label/.append style={scale=1.5}",
        "every axis plot/.style"="{
                smooth,
                mark options={scale=$(parameters["ax_plot_mark_scale"])},
                line width=$(parameters["ax_plot_line_width"])}",
        # -------------------------------------------------------------------------
        xmin=parameters["xmin"],xmax=parameters["xmax"],
        ymin=parameters["emin"],ymax=parameters["emax"],
        xtick = xtickcoords,
        xticklabels =data["x_labels"],
        xmajorgrids,
        "major x grid style={gray,thick}",
        ylabel = L"$E - E_{F}$ (eV)",
        #Legend style
        "every axis legend/.style" = "{
                                        cells={anchor=center},
                                        inner xsep=1pt,
                                        inner ysep=1pt,
                                        nodes={scale=$(parameters["ax_labels_scale"]),inner sep=2pt, transform shape},
                                        draw=none,
                                        fill=white,
                                        at={$(parameters["ax_legend_position"])},
                                        anchor=south east,
                                       }",
    },
    #spin Up
    [Plot({red,no_marks,forget_plot},Table("x"=>bands[1,:,1],"y"=>bands[1,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
    Plot({red,no_marks},Table("x"=>bands[1,:,1],"y"=>bands[1,:,parameters["final_band"]])),
    LegendEntry(L"\color{red}{Spin $\uparrow$}"),
    # fermi_level
    Plot({forget_plot, no_marks,dashed},Coordinates(xf,yf)),
    #spin down
    [Plot({blue,no_marks,forget_plot},Table("x"=>bands[2,:,1],"y"=>bands[2,:,k])) for k=parameters["initial_band"]:parameters["final_band"]-1],
    Plot({blue,no_marks},Table("x"=>bands[2,:,1],"y"=>bands[2,:,parameters["final_band"]])),
    LegendEntry(L"\color{blue}{Spin $\downarrow$}")
    ),
    )
end