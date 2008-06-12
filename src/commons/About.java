import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JButton;
import javax.swing.JTextArea;
import javax.swing.JLabel;
import javax.swing.BorderFactory;

import java.awt.BorderLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

/**
 * Shows the about window.
 *
 * Copyright: John-John Tedro, Oscar Eriksson (2008)
 *
 *   This file is part of musync-swing.
 *
 *   musync-swing is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   musync-swing is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with musync-swing.  If not, see <http://www.gnu.org/licenses/>.
 */
class About extends JFrame implements ActionListener
{
    private JButton close;
    private JPanel panel;
    private JTextArea text;

    private static final String aboutText = 
        "Authors\n" +
        "    Oscar Eriksson <oscareri@kth.se>\n" +
        "    John-John Tedro <tedro@kth.se>\n" +
        "\n" +
        "License\n" +
        "    GPLv3 or later, visit\n" +
        "    http://www.gnu.org/licenses/gpl.html";

    /**
     * Constructor created the popup but doesn't show it until
     * the method 'display' has been called.
     */
    public About() {
        super("About");
        int w = 384, h = 210;

        panel = new JPanel();
        close = new JButton("Close");
        text = new JTextArea(aboutText);
        text.setEditable(false);
        text.setBackground(null);

        panel.setLayout(new BorderLayout(2,0));
        //panel.setBorder(BorderFactory.createEmptyBorder(4,4,4,4));

        close.addActionListener(this);

        JLabel aboutImage = new JLabel("", Commons.getImageIcon("gfx/about.png"), JLabel.CENTER);
        panel.add(aboutImage, BorderLayout.CENTER);
        panel.add(close, BorderLayout.PAGE_END);

        add(panel);
        close.setSize(80,20);
        setSize(w, h);
        setDefaultCloseOperation(JFrame.HIDE_ON_CLOSE);
        Commons.center(this, w, h);
    }
    
    /**
     * What to do when the user presses 'close.'
     *
     * @param e The event
     */
    public void actionPerformed(ActionEvent e)
    {
        Object src = e.getSource();
        if (src == close)
            setVisible(false);

        return;
    }

    /*
     * Display the popup.
     */
    public void display()
    {
        this.setVisible(true);

        return;
    }
}
