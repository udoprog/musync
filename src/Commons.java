import java.io.File;
import java.io.InputStream;
import java.io.DataInputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;

import java.util.HashMap;
import java.lang.StringBuilder;

import javax.swing.JFrame;
import javax.swing.JButton;
import javax.swing.JPanel;
import javax.swing.JTextArea;
import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JLabel;
import javax.swing.JTextField;
import javax.swing.JDialog;
import javax.swing.JOptionPane;

import java.awt.Component;
import java.awt.BorderLayout;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.Toolkit;
import java.awt.Dimension;
import java.net.URL;

/**
 * Common resources in all of MusyncSwing.
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
public class Commons
{
    private static final String musync_bin = "musync";
    private static ErrorPopup errorpopup;
    public static About about;
    public static ModificationFrame tmp_meta;
    private static String[] inputs;
    private static HashMap<String, String> conf;

    // Different options input.
    public static final int INPUT_ROOT = 0, INPUT_LOG = 1;
   
    /**
     * To enable the creation of .jar files, we must use special methods to retrieve images.
     */
    public static ImageIcon getImageIcon(String url)
    {
        URL uri = Commons.class.getResource(url); 
        return new ImageIcon(uri);
    }

    /**
     * Prototype to create an actionbutton (not used).
     *
     * @return The created button.
     */
    public static javax.swing.JButton createActionButton(String text)
    {
        javax.swing.JButton button = new javax.swing.JButton(text);

        button.setIcon(getImageIcon("gfx/button.default.png"));
        button.setRolloverIcon(getImageIcon("gfx/button.rollover.png"));
        button.setPressedIcon(getImageIcon("gfx/button.pressed.png"));

        button.setBorderPainted(false);
        button.setContentAreaFilled(false);
        button.setIconTextGap(0);
        button.setMargin(new java.awt.Insets(0,0,0,0));
        button.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);

        return button;
    }

    /**
     * Build a JLabel containing the musync logotype.
     *
     * @return The created JLabel.
     */
    public static javax.swing.JLabel buildLogo()
    {
        javax.swing.ImageIcon logo_icon = Commons.getImageIcon("gfx/logo.png");
        return new javax.swing.JLabel("", logo_icon, JLabel.CENTER);
    }

    /**
     * Return the parsed configuration (or null).
     *
     * @return HashMap with configuration keys or null if none.
     */
    public static HashMap<String, String> getConfig()
    {
        return conf;
    }

    /**
     * Parse the export string recieved by musync.
     * Syntax is '<key> <value>', and value may contain spaces, key may not.
     * Export prints all configs from your musync.conf.
     *
     * @param is The inputstream related to the process.
     */
    public static void parseMusyncExport(InputStreamReader is)
    {
        BufferedReader d = new BufferedReader(is);

        if (conf == null)
            conf = new HashMap<String, String>();

        try {
            StringBuilder pri = new StringBuilder();
            int t = 0;
            boolean first = true;
            String key = null, value = null;
            while ((t = is.read()) > 0) {
                if (first) {
                    if (t == ' ') {
                        key = pri.toString();
                        pri = new StringBuilder();
                        first = false;
                    } else {
                        pri.append((char)t);
                    }
                } else {
                    if (t == '\n') {
                        value = pri.toString();
                        conf.put(key, value);
                        pri = new StringBuilder();
                        first = true;
                    } else {
                        pri.append((char)t);
                    }
                }
            }
        }
        catch (Exception ex) {
            ex.getMessage();
        }
        finally {
            try {
                is.close();
            }
            catch (Exception ex) {}
        }

        return;
    }

    /**
     * Setup all common resources.
     */
    public static void setup()
    {
        errorpopup = new ErrorPopup();
        about = new About();
        inputs = new String[2];
        tmp_meta = new ModificationFrame();
    }

    /**
     * Creates an error dialog displaying an error.
     *
     * This cannot be run before setup, since that is where it is being
     * instantiated.
     *
     * This is very similar to a normal printf
     *
     * @param format format of objects
     * @param args[] list of arguments (variadic length)
     */
    static public void epopup(String format, Object ... args)
    {
        JOptionPane.showMessageDialog(null, String.format(format, args));
    }

    /**
     * Print an error in the terminal, mainly for debugging purposes.
     * This is similar to printf.
     *
     * @param format format of objects
     * @param args[] list of arguments (variadic length)
     */
    public static void eprint(String format, Object ... args)
    {
        System.err.printf(format, args);
    }

    /**
     * Use this method to center floating JComponents.
     *
     * @param component Component to be centered.
     * @param w Components width.
     * @param h Components height.
     */
    public static void center(Component component, int w, int h)
    {
        Toolkit tk = Toolkit.getDefaultToolkit();
        Dimension screen = tk.getScreenSize();
        
        int lx = (int)(screen.getWidth()  * 1/2 - (w/2));
        int ly = (int)(screen.getHeight() * 1/2 - (h/2));
        component.setLocation(lx, ly);
    }
    
    /**
     * Create an inputdialog, this is at the moment just an overlay to swings standard methods.
     *
     * @param parentComponent Parent of dialog (this will wait for input).
     * @param message Messge to print woth the prompting.
     * @param value Initial value in the inputdialog.
     */
    public static String inputDialog(Component parentComponent, Object message, Object value)
    {
        return JOptionPane.showInputDialog(parentComponent, message, value);
    }
   
    /**
     * Checks if you have the 'musync' executable somewhere in your PATH variable.
     *
     * @return True if musync is in your PATH, false otherwise.
     */
    public static boolean checkForMusyncInPath() {
        String PATH = System.getenv("PATH");
        if (PATH == null)
            return false;

        String paths[] = PATH.split(":");
        
        for (String p : paths)
            if ((new File(p + "/" + musync_bin)).isFile())
                return true;

        return false;
    }
}
